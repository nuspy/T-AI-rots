<#--
  Il guscio di ogni pagina di accesso (login, registrazione, password dimenticata e da aggiornare, 2FA, errori,
  info) nello stile della v2 del sito: testata prugna col marchio «✦ TAROTS chat», foglio di carta chiara al centro,
  piede prugna. Riscrive solo il layout di `keycloak.v2`: le pagine (login.ftl, register.ftl, login-otp.ftl, …)
  restano quelle del tema di base, con il loro markup PatternFly, ridisegnato da css/tarots-v7.css.

  La firma della macro (`registrationLayout bodyClass displayInfo displayMessage displayRequiredFields`) e le sezioni
  annidate (header, show-username, form, info, socialProviders) sono quelle di keycloak.v2 26.0: le pagine di base
  le chiamano così, e una sezione mancante o rinominata sparirebbe senza errori. Da riallineare se si aggiorna
  l'immagine di Keycloak a una versione maggiore (vedi deploy/keycloak/README.md, «Tema»).
-->
<#import "field.ftl" as field>
<#import "footer.ftl" as loginFooter>
<#macro username>
  <#assign label>
    <#if !realm.loginWithEmailAllowed>${msg("username")}<#elseif !realm.registrationEmailAsUsername>${msg("usernameOrEmail")}<#else>${msg("email")}</#if>
  </#assign>
  <@field.group name="username" label=label>
    <div class="${properties.kcInputGroup}">
      <div class="${properties.kcInputGroupItemClass} ${properties.kcFill}">
        <span class="${properties.kcInputClass} ${properties.kcFormReadOnlyClass}">
          <input id="kc-attempted-username" value="${auth.attemptedUsername}" readonly>
        </span>
      </div>
      <div class="${properties.kcInputGroupItemClass}">
        <a id="reset-login" class="t-ricomincia" href="${url.loginRestartFlowUrl}">${msg("tarotsCambiaAccount")}</a>
      </div>
    </div>
  </@field.group>
</#macro>

<#macro registrationLayout bodyClass="" displayInfo=false displayMessage=true displayRequiredFields=false>
<!DOCTYPE html>
<html class="${properties.kcHtmlClass!}" lang="${(locale.currentLanguageTag)!'en'}"<#if realm.internationalizationEnabled> dir="${(locale.rtl)?then('rtl','ltr')}"</#if>>

<head>
    <meta charset="utf-8">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="robots" content="noindex, nofollow">
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
    <meta name="color-scheme" content="light">
    <meta name="theme-color" content="#201026">
    <#if properties.meta?has_content>
        <#list properties.meta?split(' ') as meta>
            <meta name="${meta?split('==')[0]}" content="${meta?split('==')[1]}"/>
        </#list>
    </#if>
    <title>${msg("loginTitle",(realm.displayName!''))}</title>
    <link rel="icon" href="${url.resourcesPath}/img/logo.webp" type="image/webp" />
    <link rel="preload" href="${url.resourcesPath}/fonts/dm-sans-latin.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="preload" href="${url.resourcesPath}/fonts/libre-baskerville-latin.woff2" as="font" type="font/woff2" crossorigin>
    <#if properties.stylesCommon?has_content>
        <#list properties.stylesCommon?split(' ') as style>
            <link href="${url.resourcesCommonPath}/${style}" rel="stylesheet" />
        </#list>
    </#if>
    <#if properties.styles?has_content>
        <#list properties.styles?split(' ') as style>
            <link href="${url.resourcesPath}/${style}" rel="stylesheet" />
        </#list>
    </#if>
    <script type="importmap">
        {
            "imports": {
                "rfc4648": "${url.resourcesCommonPath}/vendor/rfc4648/rfc4648.js"
            }
        }
    </script>
    <#if properties.scripts?has_content>
        <#list properties.scripts?split(' ') as script>
            <script src="${url.resourcesPath}/${script}" type="text/javascript"></script>
        </#list>
    </#if>
    <#if scripts??>
        <#list scripts as script>
            <script src="${script}" type="text/javascript"></script>
        </#list>
    </#if>
    <script type="module" src="${url.resourcesPath}/js/passwordVisibility.js"></script>
    <script type="module">
        import { startSessionPolling } from "${url.resourcesPath}/js/authChecker.js";

        startSessionPolling(
            "${url.ssoLoginInOtherTabsUrl?no_esc}"
        );
    </script>
    <script>
        /* I codici a sei cifre (OTP): tastierino numerico sul telefono e completamento dal messaggio/app. */
        document.addEventListener("DOMContentLoaded", function () {
            ["otp", "totp"].forEach(function (id) {
                var campo = document.getElementById(id);
                if (campo) {
                    campo.setAttribute("inputmode", "numeric");
                    campo.setAttribute("autocomplete", "one-time-code");
                    campo.setAttribute("pattern", "[0-9]*");
                }
            });
        });
    </script>
</head>

<body id="keycloak-bg" class="t-corpo ${bodyClass}">
<a class="t-salta" href="#kc-page-title">${msg("tarotsSaltaAlModulo")}</a>

<header class="t-testata">
    <#if client?? && client.baseUrl?has_content>
        <a class="t-marchio" href="${client.baseUrl}" aria-label="${msg('tarotsTornaAlSito')}">
            <span class="t-marchio-segno" aria-hidden="true">✦</span>
            <span>TAROTS <em>chat</em></span>
        </a>
    <#else>
        <span class="t-marchio">
            <span class="t-marchio-segno" aria-hidden="true">✦</span>
            <span>TAROTS <em>chat</em></span>
        </span>
    </#if>
    <#if realm.internationalizationEnabled && locale.supported?size gt 1>
        <div class="t-lingua">
            <label class="t-nascosto" for="login-select-toggle">${msg("languages")}</label>
            <select id="login-select-toggle" onchange="if (this.value) window.location.href=this.value">
                <#list locale.supported?sort_by("label") as l>
                    <option value="${l.url}" ${(l.languageTag == locale.currentLanguageTag)?then('selected','')}>${l.label}</option>
                </#list>
            </select>
        </div>
    </#if>
</header>

<div class="t-scena">
    <aside class="t-quinta" aria-hidden="true">
        <div class="t-cerchio"></div>
        <p class="t-occhiello t-occhiello-chiaro">TAROTS chat</p>
        <p class="t-motto">${msg("tarotsMotto")}</p>
    </aside>

    <main class="t-foglio">
        <p class="t-occhiello">${msg("tarotsOcchiello")}</p>
        <h1 class="t-titolo" id="kc-page-title" tabindex="-1"><#nested "header"></h1>

        <#if !(auth?has_content && auth.showUsername() && !auth.showResetCredentials())>
            <#if displayRequiredFields>
                <p class="t-obbligatori">
                    <span class="${properties.kcInputRequiredClass!}">*</span> ${msg("requiredFields")}
                </p>
            </#if>
        <#else>
            <#if displayRequiredFields>
                <p class="t-obbligatori">
                    <span class="${properties.kcInputRequiredClass!}">*</span> ${msg("requiredFields")}
                </p>
            </#if>
            <#-- Niente riga «Email: … Non sei tu? Cambia» dei passi dopo il primo (password, codice della 2FA): decisione
                 dell'operatore del 28/9, ribadita il 5/10 («richiesta inutile dell'email»). La macro `username` resta
                 qui sopra, non usata, per riallineare il guscio a keycloak.v2 senza cercarla. -->
            <div class="${properties.kcFormClass} t-chi">
                <#nested "show-username">
            </div>
        </#if>

        <#-- Le azioni avviate dall'app (attivare la 2FA dal profilo) non vedono gli avvisi «devi completare…». -->
        <#if displayMessage && message?has_content && (message.type != 'warning' || !isAppInitiatedAction??)>
            <div class="t-avviso t-avviso-${message.type}" role="<#if message.type = 'error'>alert<#else>status</#if>">
                <span class="t-avviso-segno" aria-hidden="true"><#if message.type = 'success'>✓<#elseif message.type = 'error'>!<#else>i</#if></span>
                <span class="kc-feedback-text">${kcSanitize(message.summary)?no_esc}</span>
            </div>
        </#if>

        <#nested "form">

        <#if auth?has_content && auth.showTryAnotherWayLink()>
            <form id="kc-select-try-another-way-form" action="${url.loginAction}" method="post" novalidate="novalidate">
                <input type="hidden" name="tryAnotherWay" value="on"/>
                <button id="try-another-way" type="submit" class="t-bottone-quieto">
                    ${kcSanitize(msg("doTryAnotherWay"))?no_esc}
                </button>
            </form>
        </#if>

        <#nested "socialProviders">

        <#if displayInfo>
            <div id="kc-info" class="t-info">
                <div id="kc-info-wrapper">
                    <#nested "info">
                </div>
            </div>
        </#if>
    </main>
</div>

<footer class="t-piede">
    <p>${msg("tarotsPiede")}</p>
    <#if client?? && client.baseUrl?has_content>
        <a href="${client.baseUrl}">${msg("tarotsTornaAlSito")}</a>
    </#if>
    <@loginFooter.content/>
</footer>
</body>
</html>
</#macro>
