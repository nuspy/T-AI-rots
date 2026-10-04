package chat.tarots.keycloak;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

import org.jboss.logging.Logger;
import org.keycloak.authentication.AuthenticationFlowContext;
import org.keycloak.authentication.authenticators.broker.AbstractIdpAuthenticator;
import org.keycloak.authentication.authenticators.broker.util.SerializedBrokeredIdentityContext;
import org.keycloak.broker.provider.BrokeredIdentityContext;
import org.keycloak.common.util.Time;
import org.keycloak.credential.CredentialModel;
import org.keycloak.models.FederatedIdentityModel;
import org.keycloak.models.IdentityProviderModel;
import org.keycloak.models.KeycloakSession;
import org.keycloak.models.RealmModel;
import org.keycloak.models.UserModel;
import org.keycloak.models.UserSessionModel;

/**
 * Collega l'identità social all'utente che ha già la stessa email, come «Automatically set existing user» di
 * Keycloak, ma senza consegnare l'account a chi l'aveva creato senza mai confermare l'email.
 *
 * Il caso: un intruso si registra con email e password usando l'email di un altro, e non la verifica (non può).
 * Quando il vero titolare entra con Google, il collegamento automatico gli darebbe quell'account, e l'intruso
 * continuerebbe a entrare con la sua password. Qui, se l'email dell'utente esistente <b>non è verificata</b>, prima
 * di collegare si tolgono i suoi vecchi accessi:
 * <ul>
 *   <li>nome e cognome, che diventano quelli del social (se li dà);</li>
 *   <li>tutte le credenziali salvate (password, OTP, chiavi di sicurezza);</li>
 *   <li>i collegamenti con i social che non garantiscono l'email (X, Microsoft: chiunque può scriverci l'email di un
 *   altro);</li>
 *   <li>le sessioni aperte, anche quelle offline del login persistente, e i token già emessi (not-before).</li>
 * </ul>
 * L'email diventa verificata: il provider di questo accesso la garantisce (il flusso si assegna solo ai provider con
 * {@code trustEmail}, e qui lo si ricontrolla). Cosa è stato tolto lo si dice al sito con una nota della sessione
 * ({@link #NOTA}, nel token come claim {@code tarots_unione}): il sito chiede alla persona se l'account era suo.
 *
 * Con l'email già verificata non cambia niente rispetto al collegamento automatico di Keycloak: chi l'aveva creato ha
 * dimostrato di leggere quella casella, quindi è la stessa persona.
 */
public class UnioneSicuraAuthenticator extends AbstractIdpAuthenticator {

    private static final Logger LOG = Logger.getLogger(UnioneSicuraAuthenticator.class);

    /** La nota di sessione (e il claim) con cosa è stato tolto: {@code istante|creato|credenziali|social}. */
    public static final String NOTA = "tarots_unione";

    @Override
    protected void authenticateImpl(AuthenticationFlowContext context, SerializedBrokeredIdentityContext serializedCtx,
                                    BrokeredIdentityContext brokerContext) {
        KeycloakSession session = context.getSession();
        RealmModel realm = context.getRealm();
        UserModel utente = getExistingUser(session, realm, context.getAuthenticationSession());
        IdentityProviderModel provider = brokerContext.getIdpConfig();

        if (!utente.isEmailVerified()) {
            if (provider == null || !provider.isTrustEmail() || !stessaEmail(utente.getEmail(), brokerContext.getEmail())) {
                // Non dovrebbe succedere (il flusso è solo dei provider fidati, e l'utente esistente si trova per
                // email): ma senza la garanzia dell'email non si può togliere niente a nessuno, né collegare.
                LOG.warnf("Unione rifiutata: email non garantita da '%s' per l'utente %s", provider == null ? "?" : provider.getAlias(), utente.getId());
                context.attempted();
                return;
            }
            String nota = togliVecchiAccessi(session, realm, utente, provider.getAlias());
            // Nome e cognome li aveva scritti chi ha creato l'account: valgono quelli del social, se li dà.
            if (nonVuoto(brokerContext.getFirstName())) {
                utente.setFirstName(brokerContext.getFirstName());
            }
            if (nonVuoto(brokerContext.getLastName())) {
                utente.setLastName(brokerContext.getLastName());
            }
            if (nota != null) {
                context.getAuthenticationSession().setUserSessionNote(NOTA, nota);
            }
        }
        context.setUser(utente);
        context.success();
    }

    private static boolean nonVuoto(String testo) {
        return testo != null && !testo.isBlank();
    }

    private static boolean stessaEmail(String a, String b) {
        return a != null && b != null && a.trim().equalsIgnoreCase(b.trim());
    }

    /** Toglie ciò con cui si poteva entrare prima di questo accesso. Restituisce la nota, o null se non c'era niente. */
    static String togliVecchiAccessi(KeycloakSession session, RealmModel realm, UserModel utente, String questoProvider) {
        List<String> credenziali = new ArrayList<>();
        for (CredentialModel c : utente.credentialManager().getStoredCredentialsStream().collect(Collectors.toList())) {
            if (utente.credentialManager().removeStoredCredentialById(c.getId()) && !credenziali.contains(c.getType())) {
                credenziali.add(c.getType());
            }
        }

        List<String> social = new ArrayList<>();
        for (FederatedIdentityModel link : session.users().getFederatedIdentitiesStream(realm, utente).collect(Collectors.toList())) {
            String alias = link.getIdentityProvider();
            if (alias.equals(questoProvider)) {
                continue;
            }
            IdentityProviderModel altro = session.identityProviders().getByAlias(alias);
            if (altro == null || !altro.isTrustEmail()) {
                session.users().removeFederatedIdentity(realm, utente, alias);
                social.add(alias);
            }
        }

        // Fuori chi era dentro: sessioni normali e offline, e ogni token emesso fino a questo secondo.
        for (UserSessionModel s : session.sessions().getUserSessionsStream(realm, utente).collect(Collectors.toList())) {
            session.sessions().removeUserSession(realm, s);
        }
        for (UserSessionModel s : session.sessions().getOfflineUserSessionsStream(realm, utente).collect(Collectors.toList())) {
            session.sessions().removeOfflineUserSession(realm, s);
        }
        session.users().setNotBeforeForUser(realm, utente, Time.currentTime());

        utente.removeRequiredAction(UserModel.RequiredAction.VERIFY_EMAIL);
        utente.setEmailVerified(true);

        if (credenziali.isEmpty() && social.isEmpty()) {
            return null;
        }
        LOG.infof("Unione: tolti all'utente %s le credenziali %s e i social %s", utente.getId(), credenziali, social);
        Long creato = utente.getCreatedTimestamp();
        return Time.currentTime() + "|" + (creato == null ? "" : String.valueOf(creato / 1000)) + "|"
                + String.join(",", credenziali) + "|" + String.join(",", social);
    }

    @Override
    protected void actionImpl(AuthenticationFlowContext context, SerializedBrokeredIdentityContext serializedCtx,
                              BrokeredIdentityContext brokerContext) {
        authenticateImpl(context, serializedCtx, brokerContext);
    }

    @Override
    public boolean requiresUser() {
        return false;
    }

    @Override
    public boolean configuredFor(KeycloakSession session, RealmModel realm, UserModel user) {
        return true;
    }
}
