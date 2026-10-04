package chat.tarots.keycloak;

import java.util.Collections;
import java.util.List;

import org.keycloak.Config;
import org.keycloak.authentication.Authenticator;
import org.keycloak.authentication.AuthenticatorFactory;
import org.keycloak.models.AuthenticationExecutionModel;
import org.keycloak.models.KeycloakSession;
import org.keycloak.models.KeycloakSessionFactory;
import org.keycloak.provider.ProviderConfigProperty;

/** Il passo «Collega l'utente esistente, togliendo i vecchi accessi se l'email non era verificata». */
public class UnioneSicuraAuthenticatorFactory implements AuthenticatorFactory {

    /** L'id del passo nei flussi: lo usano il backend (`assicura_flusso_unione`) e il generatore del realm. */
    public static final String ID = "tarots-unione-sicura";

    private static final AuthenticationExecutionModel.Requirement[] SCELTE = {
        AuthenticationExecutionModel.Requirement.REQUIRED,
        AuthenticationExecutionModel.Requirement.ALTERNATIVE,
        AuthenticationExecutionModel.Requirement.DISABLED,
    };

    private static final UnioneSicuraAuthenticator ISTANZA = new UnioneSicuraAuthenticator();

    @Override
    public String getId() {
        return ID;
    }

    @Override
    public String getDisplayType() {
        return "TAROTS: collega l'utente esistente in sicurezza";
    }

    @Override
    public String getHelpText() {
        return "Come «Automatically set existing user», ma se l'email dell'utente esistente non è verificata ne toglie "
                + "prima password, OTP, social non fidati e sessioni, e la segna come verificata.";
    }

    @Override
    public String getReferenceCategory() {
        return "autoLink";
    }

    @Override
    public boolean isConfigurable() {
        return false;
    }

    @Override
    public AuthenticationExecutionModel.Requirement[] getRequirementChoices() {
        return SCELTE;
    }

    @Override
    public boolean isUserSetupAllowed() {
        return false;
    }

    @Override
    public List<ProviderConfigProperty> getConfigProperties() {
        return Collections.emptyList();
    }

    @Override
    public Authenticator create(KeycloakSession session) {
        return ISTANZA;
    }

    @Override
    public void init(Config.Scope config) {
    }

    @Override
    public void postInit(KeycloakSessionFactory factory) {
    }

    @Override
    public void close() {
    }
}
