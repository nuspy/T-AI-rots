/* Metodo e privacy: i contenuti legali del sito (stesso titolare, stesse scelte, stesse statistiche), più che cosa
 * ricorda il lettore e come si usa l'AI. */

import type { privacy as Base } from "../en/privacy";

export const privacy: typeof Base = {
  meta_titolo: "Método y privacidad",
  meta_descrizione: "Qué se guarda, por qué y cómo decides tú: lecturas, memoria, estadísticas y cookies.",
  eyebrow: "Método y privacidad",
  titolo: "Místico no tiene por qué significar opaco.",
  intro: "Qué se guarda, por qué y cómo decides tú. Las mismas reglas se aplican a todas las páginas de TAROTS chat.",

  letture_titolo: "Tus lecturas y tu memoria",
  letture_testo: "Las lecturas se guardan en tu cuenta para que puedas volver a ellas. Lo que recuerda tu lector procede de tus lecturas y conversaciones, y puedes revisarlo, editarlo o borrarlo en cualquier momento desde Mi historia. Borrar una lectura la elimina para siempre.",
  letture_cta: "Gestionar lo que se recuerda",
  ai_titolo: "Cómo se usa la IA",
  ai_testo: "Una IA interpreta las cartas en el contexto de tu pregunta y de tus palabras. Los nombres nunca llegan al proveedor de la IA: recibe un marcador («Persona_1») y tú lees el nombre real; el apellido de la otra persona nunca se envía. La IA no conoce el futuro y ninguna lectura es una predicción. En cada petición pedimos al proveedor que no conserve las respuestas: tus textos no se quedan con él para entrenar sus modelos.",

  custode_titolo: "Quién es responsable de tus datos",
  // Los datos del responsable vienen de la consola (Impostazioni → Dati del titolare): la página rellena los
  // {marcadores}, y un campo vacío muestra la frase neutra de al lado.
  custode_testo: "El responsable del tratamiento de los datos personales recogidos por TAROTS chat (https://tarots.chat) es {titolare}.",
  custode_testo_senza_nome: "Con el responsable del tratamiento de los datos personales recogidos por TAROTS chat (https://tarots.chat) se contacta en la dirección de privacidad que aparece abajo.",
  custode_indirizzo: "Dirección postal: {indirizzo}.",
  custode_indirizzo_vuoto: "Dirección postal: disponible a petición en el contacto de privacidad.",
  custode_codice: "NIF o número de IVA: {codice}.",
  custode_email: "Contacto de privacidad: {email}",
  custode_email_vuoto: "Contacto de privacidad: en actualización; mientras tanto puedes ejercer tus derechos desde tu cuenta.",
  custode_dpo: "Delegado de protección de datos (DPO): {dpo}.",
  custode_dpo_no: "No se ha designado un delegado de protección de datos (DPO).",

  scelte_titolo: "Tus elecciones en este navegador",
  scelte_testo: "Todo lo que ves aquí abajo queda apagado hasta que lo enciendas, y puedes cambiarlo aquí cuando quieras. Las cookies técnicas (el acceso, la lectura gratuita sin cuenta, el recuerdo de estas elecciones) no necesitan consentimiento: sin ellas el sitio no funciona.",
  scelte_account: "Las elecciones que afectan a tu cuenta — tus palabras para estadísticas, los datos sensibles, las promociones — están en tu cuenta.",
  scelte_account_cta: "Privacidad y consentimientos",

  finalita_titolo: "Qué usamos, por qué y con qué base jurídica",
  finalita_intro: "Cada uso de tus datos tiene su propia finalidad y su propia base jurídica según el RGPD:",
  finalita: [
    { cosa: "Cuenta y perfil", perche: "Para darte una cuenta, conservar tus lecturas y tus cartas personales, y dejarte entrar (también con una red social).", base: "Base: el contrato que pides (art. 6.1.b RGPD)." },
    { cosa: "Lecturas, entrevista, memoria y chat", perche: "Para leerte las cartas con una IA y recordar lo que ayuda en las lecturas siguientes.", base: "Base: contrato; para los datos sensibles, tu consentimiento explícito (art. 9.2.a)." },
    { cosa: "La lectura gratuita sin cuenta", perche: "Para que pruebes una lectura antes de registrarte.", base: "Base: medidas precontractuales que pides tú (art. 6.1.b)." },
    { cosa: "Pagos, créditos, pedidos y envíos", perche: "Para vender créditos, planes y mazos, y llevar la contabilidad que exige la ley.", base: "Base: contrato y obligaciones legales (art. 6.1.b y 6.1.c)." },
    { cosa: "Seguridad y registros", perche: "Para proteger las cuentas y el servicio, y saber quién hizo qué. Las direcciones IP solo se guardan acortadas, con una huella cifrada con clave.", base: "Base: interés legítimo (art. 6.1.f)." },
    { cosa: "Estadísticas anónimas", perche: "Para contar las visitas sin cookies y sin guardar nada en tu navegador.", base: "Base: interés legítimo." },
    { cosa: "Estadísticas vinculadas a tu cuenta", perche: "Para entender qué canales traen miembros y qué lleva a una compra.", base: "Base: interés legítimo; puedes oponerte desde tu cuenta (art. 21)." },
    { cosa: "Estadísticas del sitio con un identificador del navegador", perche: "Para reconocer tu navegador cuando vuelves.", base: "Base: tu consentimiento (art. 6.1.a)." },
    { cosa: "Google Analytics", perche: "Para medir cómo se usa el sitio.", base: "Base: tu consentimiento." },
    { cosa: "Publicidad", perche: "Para mostrar anuncios de Google AdSense en unos pocos espacios marcados, solo si están activados.", base: "Base: tu consentimiento." },
    { cosa: "Tus palabras para estadísticas e ideas del blog", perche: "Para entender, de forma anónima y agregada, qué temas importan a las personas (sin citar nunca a nadie). Todavía no está activo.", base: "Base: tu consentimiento, separado y opcional." },
    { cosa: "Promociones", perche: "Ofertas y novedades con notificaciones, cuando lleguen.", base: "Base: tu consentimiento." },
    { cosa: "Edad mínima", perche: "Para comprobar que tienes edad para usar el servicio por tu cuenta.", base: "Base: obligación legal (art. 8 RGPD) y contrato." },
  ],

  art9_titolo: "Datos sensibles",
  art9_testo: "Algunas cosas que puedes contarnos son categorías especiales de datos: ser una persona trans, tu salud. La casilla «persona trans» y los recuerdos sobre tu salud solo se usan con tu consentimiento explícito, que das donde marcas la casilla y que puedes retirar cuando quieras desde tu cuenta: entonces la casilla se vacía y esos recuerdos se borran. Sin él, nunca llegan a la IA.",
  art9_crisi: "Si escribes que quieres hacerte daño, la lectura se detiene y te mostramos enseguida dónde encontrar ayuda. Solo contamos que ha ocurrido, sin vincularlo a ti.",

  stat_titolo: "Estadísticas de uso",
  stat_anonime: "Medimos de forma anónima cómo se usa el sitio: páginas visitadas, de dónde llega la visita (buscador, red social, campaña), tipo de dispositivo y de navegador, país y ciudad aproximados. Sin cookies y sin guardar nada en tu navegador. Tu dirección IP solo se usa en el momento de la visita, para estimar el país y la ciudad y para calcular una huella que cambia cada día: nunca se guarda.",
  stat_account: "Si tienes una cuenta y has iniciado sesión, tus visitas se vinculan a tu cuenta, sobre la base de nuestro interés legítimo en entender cómo mejorar el servicio (por ejemplo, de qué canal llegan los nuevos miembros y qué lleva a una compra). Puedes oponerte en cualquier momento desde tu cuenta: a partir de entonces las visitas dejan de vincularse y se borra el vínculo con las anteriores.",
  stat_esteso: "Si activas «Estadísticas del sitio», también reconocemos tu navegador cuando vuelves en días posteriores, con un identificador aleatorio guardado en tu navegador. Si lo rechazas o cambias de opinión, nuestros servidores también olvidan el identificador.",
  stat_google: "Si activas «Google Analytics», también usamos Google Analytics 4, un servicio de Google Ireland Ltd., que instala sus propias cookies (_ga) para contar las visitas y entender cómo se usa el sitio. Solo se carga después de tu consentimiento (Google Consent Mode), con las señales de Google y la personalización de anuncios desactivadas; Google Analytics 4 no almacena direcciones IP. Google puede tratar los datos en Estados Unidos en el marco del EU-US Data Privacy Framework. Si rechazas o retiras tu consentimiento, Google Analytics se detiene y sus cookies se eliminan.",
  stat_conservazione: "Las visitas y los eventos detallados se conservan durante 25 meses; después solo quedan totales diarios anónimos. Los análisis automáticos y las exportaciones solo usan datos agregados.",
  stat_geo: "Geolocalización por IP:",
  pubblicita_titolo: "Publicidad",
  pubblicita_testo: "Algunas páginas pueden mostrar hasta tres espacios marcados como «Publicidad», que llena Google AdSense, un servicio de Google Ireland Ltd. Los anuncios solo se cargan si aceptas aquí o en el aviso: entonces Google instala sus propias cookies (como __gads y __gpi) para servir los anuncios, limitar cuántas veces los ves y medirlos, y puede tratar los datos en Estados Unidos en el marco del EU-US Data Privacy Framework. Los anuncios no son personalizados salvo que esta página indique lo contrario. Si no aceptas, los espacios no aparecen y no se carga nada de Google AdSense.",

  social_titolo: "Entrar con una red social",
  social_account: "Una cuenta por persona: si entras con Google, Facebook, Apple, GitHub o LinkedIn con el mismo correo de una cuenta que ya existe, es la misma cuenta, con las mismas lecturas y los mismos créditos.",
  social_cosa: "De esa cuenta recibimos lo que comparte con nosotros: nombre y apellidos, correo, foto de perfil, idioma y — solo si lo permites en la pantalla del proveedor — fecha de nacimiento, género y ciudad. Los usamos solo para rellenar los campos de tu cuenta todavía vacíos, nunca encima de lo que escribiste tú.",
  social_perche: "Por qué: de la fecha de nacimiento salen tus cartas personales (la carta del alma y la del año) y el género sirve para pronombres y concordancias en las lecturas de pareja; nombre, idioma y foto te ahorran volver a escribirlos. Base jurídica: el servicio que pides y tu elección en la pantalla del proveedor.",
  social_posizione: "Ubicación actual: país y ciudad, de la red social si los comparte; si no, estimados en cada acceso a partir de tu dirección IP con una base de datos que está en nuestro servidor (la dirección no se guarda y nada va a terceros). Nos ayuda a adaptar el servicio.",
  social_controllo: "Desde tu cuenta ves de dónde viene cada dato, lo corriges o lo borras, detienes la importación o la ubicación, o borras de una vez todo lo que llegó de las redes sociales. Las redes vinculadas se gestionan en los ajustes de la cuenta («Cuentas vinculadas»).",
  social_cta: "Gestiona tus datos",

  responsabili_titolo: "Quién más trata tus datos, y dónde",
  responsabili_intro: "No vendemos tus datos ni los compartimos con socios. Estos proveedores los tratan por cuenta nuestra, o como responsables independientes cuando eliges usarlos:",
  responsabili: [
    { chi: "Alojamiento", cosa: "nuestro servidor y la base de datos. Proveedor y ubicación: {hosting}." },
    { chi: "Proveedores de IA", cosa: "los proveedores de modelos de lenguaje que configuramos reciben el texto de tu pregunta, de la entrevista y del chat — con los nombres sustituidos por un marcador y nunca el apellido — solo para escribir la lectura. Proveedores actuales y países: {fornitori_ai}." },
    { chi: "Google", cosa: "Google Analytics y AdSense (solo con tu consentimiento) y el acceso con Google (Google Ireland Ltd., los datos pueden ir a Estados Unidos)." },
    { chi: "Acceso con redes sociales", cosa: "Apple, Facebook (Meta), GitHub y LinkedIn, solo si eliges entrar con ellos: son responsables independientes de tu cuenta con ellos." },
    { chi: "Pagos", cosa: "Stripe, para los pagos con tarjeta (Stripe Payments Europe, los datos pueden ir a Estados Unidos). Nunca vemos el número de tu tarjeta." },
    { chi: "Notificaciones de la app", cosa: "Firebase Cloud Messaging (Google), para las notificaciones de la app, cuando lleguen." },
    { chi: "Correo y copias de seguridad", cosa: "el correo que escribes a una dirección @tarots.chat pasa por el servicio de reenvío de Namecheap (Estados Unidos) y llega a un buzón de Gmail del responsable (Google); los correos que te enviamos salen de nuestro propio servidor, alojado por Hivelocity en Londres; las copias de seguridad están en nuestro propio almacenamiento en Italia, sin terceros." },
  ],
  hosting_vuoto: "un proveedor vinculado por un acuerdo de tratamiento de datos",
  fornitori_ai_vuoto: "ninguno activo en este momento",
  fornitori_ai_proprio: "en un servidor nuestro, sin terceros",
  trasferimenti: "Cuando los datos salen del Espacio Económico Europeo nos basamos en una decisión de adecuación de la Comisión Europea (el Reino Unido; Estados Unidos para las empresas certificadas en el EU-US Data Privacy Framework) o en las cláusulas contractuales tipo de la Comisión.",

  conservazione_titolo: "Cuánto tiempo los conservamos",
  conservazione: [
    "Cuenta, lecturas, memoria y chat: hasta que los borres tú o borres tu cuenta. No hay una caducidad automática: también podemos borrar nosotros datos antiguos, por ejemplo las lecturas gratuitas sin cuenta y los chats antiguos.",
    "La lectura gratuita sin cuenta: hasta que la borremos; si te registras, pasa a formar parte de tu cuenta.",
    "Estadísticas detalladas de las visitas: 25 meses, después solo totales diarios anónimos.",
    "Tus elecciones sobre los consentimientos: el tiempo necesario para poder demostrarlas.",
    "Registros contables (pagos, créditos, pedidos): el tiempo que exige la ley (en Italia, diez años). Si borras tu cuenta, quedan separados de tu identidad.",
    "Copias de seguridad: los datos borrados desaparecen de las copias a medida que rotan, en una semana aproximadamente.",
  ],

  diritti_titolo: "Tus derechos",
  diritti_testo: "Puedes pedir acceder a tus datos, corregirlos, borrarlos, recibirlos en un formato portable, limitar su uso u oponerte a él, y retirar cualquier consentimiento en cualquier momento — sin que eso afecte a lo que se hizo antes.",
  diritti_come: "Casi todo puedes hacerlo tú: descargar tus datos y eliminar tu cuenta desde la página de tu cuenta, y cambiar cada consentimiento allí o en esta página. Para todo lo demás, escribe al contacto de privacidad indicado arriba: respondemos en el plazo de un mes.",
  diritti_cta_dati: "Tus datos y consentimientos",
  diritti_cta_elimina: "Elimina tu cuenta",
  garante_titolo: "Reclamaciones",
  garante_testo: "Si crees que tus datos se tratan de forma ilícita, puedes presentar una reclamación ante la autoridad italiana de protección de datos, el Garante per la protezione dei dati personali (www.garanteprivacy.it), o ante la autoridad del país donde vives o trabajas.",

  eta_titolo: "Edad mínima",
  eta_testo: "TAROTS chat es para personas de 16 años o más; 14 en Italia y en España, 15 en Francia — la edad a partir de la cual la ley te permite usar por tu cuenta los servicios en línea. Te pedimos que la confirmes antes de la primera lectura. Si la fecha de nacimiento de tu cuenta está por debajo del mínimo, las lecturas y el chat se detienen.",

  versione: "Versión 3 — 3 de octubre de 2026.",
};
