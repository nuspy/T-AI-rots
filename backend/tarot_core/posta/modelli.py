"""I testi delle email agli utenti, nelle sei lingue del sito (v9, Fase 2b).

Ogni modello ha l'oggetto, un titolo, i paragrafi e il pulsante; i valori variabili si scrivono `{nome}` e li riempie
`posta.invio`: `{piano}` (il nome del piano), `{data}` (una scadenza), `{importo}` (già formattato con la valuta),
`{giorni}`, `{sconto}` (percentuale), `{oggi}`. Il russo e l'ucraino danno del tu, come il sito.

Le email dicono sempre **quando** e **quanto**, e come tornare indietro: sono quelle che un utente rilegge quando
trova un addebito sull'estratto conto.
"""
from __future__ import annotations

from typing import Dict, List, TypedDict

LINGUE = ("en", "it", "hu", "ru", "uk", "es")


class Modello(TypedDict):
    oggetto: str
    titolo: str
    paragrafi: List[str]
    pulsante: str


#: Il piede comune: perché arriva questa email, e che non si risponde alla cieca.
PIEDE: Dict[str, str] = {
    "en": "You are receiving this email because you have a TAROTS chat subscription. It concerns your account and "
          "payments, so it is sent even if you have not agreed to marketing emails.",
    "it": "Ricevi questa email perché hai un abbonamento a TAROTS chat. Riguarda il tuo account e i pagamenti, per "
          "questo arriva anche se non hai accettato le comunicazioni promozionali.",
    "hu": "Azért kapod ezt az e-mailt, mert TAROTS chat előfizetésed van. A fiókodról és a fizetésekről szól, ezért "
          "akkor is megkapod, ha nem kértél marketing-leveleket.",
    "ru": "Ты получаешь это письмо, потому что у тебя есть подписка TAROTS chat. Оно касается твоего аккаунта и "
          "платежей, поэтому приходит, даже если ты не соглашался на рекламные рассылки.",
    "uk": "Ти отримуєш цей лист, бо маєш підписку TAROTS chat. Він стосується твого акаунта й платежів, тому "
          "надходить, навіть якщо ти не погоджувався на рекламні розсилки.",
    "es": "Recibes este correo porque tienes una suscripción a TAROTS chat. Trata sobre tu cuenta y tus pagos, por "
          "eso llega aunque no hayas aceptado comunicaciones promocionales.",
}

MODELLI: Dict[str, Dict[str, Modello]] = {
    # -- la disdetta del rinnovo automatico: una conferma formale -------------------------------------------------
    "rinnovo_spento": {
        "en": {
            "oggetto": "Confirmation: automatic renewal turned off",
            "titolo": "Automatic renewal is off",
            "paragrafi": [
                "We confirm that on {oggi} the automatic renewal of your {piano} subscription was turned off.",
                "Your subscription stays active until {data}: until then you keep all your included readings. "
                "After that date nothing more will be charged.",
                "Changed your mind? You can turn automatic renewal back on from your profile until {data}, and keep "
                "the automatic-renewal discount.",
                "If you did not make this change, reply to this email and we will look into it.",
            ],
            "pulsante": "Manage your subscription",
        },
        "it": {
            "oggetto": "Conferma: rinnovo automatico disattivato",
            "titolo": "Il rinnovo automatico è disattivato",
            "paragrafi": [
                "Ti confermiamo che il {oggi} il rinnovo automatico del tuo abbonamento {piano} è stato disattivato.",
                "L'abbonamento resta attivo fino al {data}: fino ad allora hai tutte le letture comprese. Dopo quella "
                "data non ti verrà addebitato più nulla.",
                "Hai cambiato idea? Puoi riattivare il rinnovo automatico dal tuo profilo fino al {data}, mantenendo "
                "lo sconto del rinnovo automatico.",
                "Se non sei stato tu, rispondi a questa email e verificheremo.",
            ],
            "pulsante": "Gestisci l'abbonamento",
        },
        "hu": {
            "oggetto": "Megerősítés: az automatikus megújítás kikapcsolva",
            "titolo": "Az automatikus megújítás ki van kapcsolva",
            "paragrafi": [
                "Megerősítjük, hogy {oggi} napon kikapcsoltad a(z) {piano} előfizetésed automatikus megújítását.",
                "Az előfizetésed {data} napig aktív marad: addig minden benne foglalt olvasásod megvan. Ezután nem "
                "terhelünk semmit.",
                "Meggondoltad magad? {data} napig a profilodban újra bekapcsolhatod az automatikus megújítást, és "
                "megmarad az automatikus megújítás kedvezménye.",
                "Ha nem te voltál, válaszolj erre az e-mailre, és utánanézünk.",
            ],
            "pulsante": "Előfizetés kezelése",
        },
        "ru": {
            "oggetto": "Подтверждение: автопродление отключено",
            "titolo": "Автопродление отключено",
            "paragrafi": [
                "Подтверждаем: {oggi} ты отключил автопродление подписки {piano}.",
                "Подписка остаётся активной до {data}: до этого дня у тебя есть все включённые расклады. После этой "
                "даты мы больше ничего не спишем.",
                "Передумал? До {data} ты можешь снова включить автопродление в профиле и сохранить скидку за "
                "автопродление.",
                "Если это был не ты, ответь на это письмо, и мы разберёмся.",
            ],
            "pulsante": "Управлять подпиской",
        },
        "uk": {
            "oggetto": "Підтвердження: автоподовження вимкнено",
            "titolo": "Автоподовження вимкнено",
            "paragrafi": [
                "Підтверджуємо: {oggi} ти вимкнув автоподовження підписки {piano}.",
                "Підписка залишається активною до {data}: до цього дня в тебе є всі включені розклади. Після цієї "
                "дати ми більше нічого не спишемо.",
                "Передумав? До {data} ти можеш знову ввімкнути автоподовження в профілі й зберегти знижку за "
                "автоподовження.",
                "Якщо це був не ти, відповідай на цей лист, і ми розберемося.",
            ],
            "pulsante": "Керувати підпискою",
        },
        "es": {
            "oggetto": "Confirmación: renovación automática desactivada",
            "titolo": "La renovación automática está desactivada",
            "paragrafi": [
                "Te confirmamos que el {oggi} se desactivó la renovación automática de tu suscripción {piano}.",
                "Tu suscripción sigue activa hasta el {data}: hasta entonces conservas todas tus lecturas incluidas. "
                "Después de esa fecha no se te cobrará nada más.",
                "¿Has cambiado de idea? Puedes reactivar la renovación automática desde tu perfil hasta el {data} y "
                "conservar el descuento de renovación automática.",
                "Si no has sido tú, responde a este correo y lo revisaremos.",
            ],
            "pulsante": "Gestionar la suscripción",
        },
    },
    # -- il rinnovo riacceso ---------------------------------------------------------------------------------------
    "rinnovo_riacceso": {
        "en": {
            "oggetto": "Automatic renewal is back on",
            "titolo": "Welcome back",
            "paragrafi": [
                "Automatic renewal of your {piano} subscription is on again.",
                "On {data} we will renew it for {importo}, with the automatic-renewal discount. You can turn it off "
                "from your profile at any time before then.",
            ],
            "pulsante": "Manage your subscription",
        },
        "it": {
            "oggetto": "Il rinnovo automatico è di nuovo attivo",
            "titolo": "Bentornato",
            "paragrafi": [
                "Il rinnovo automatico del tuo abbonamento {piano} è di nuovo attivo.",
                "Il {data} lo rinnoveremo a {importo}, con lo sconto del rinnovo automatico. Puoi disattivarlo dal "
                "profilo quando vuoi prima di quella data.",
            ],
            "pulsante": "Gestisci l'abbonamento",
        },
        "hu": {
            "oggetto": "Az automatikus megújítás ismét be van kapcsolva",
            "titolo": "Örülünk, hogy maradsz",
            "paragrafi": [
                "A(z) {piano} előfizetésed automatikus megújítása ismét be van kapcsolva.",
                "{data} napon {importo} összegért megújítjuk, az automatikus megújítás kedvezményével. Addig bármikor "
                "kikapcsolhatod a profilodban.",
            ],
            "pulsante": "Előfizetés kezelése",
        },
        "ru": {
            "oggetto": "Автопродление снова включено",
            "titolo": "Рады, что ты остаёшься",
            "paragrafi": [
                "Автопродление подписки {piano} снова включено.",
                "{data} мы продлим её за {importo} со скидкой за автопродление. До этого дня ты можешь отключить его "
                "в профиле в любой момент.",
            ],
            "pulsante": "Управлять подпиской",
        },
        "uk": {
            "oggetto": "Автоподовження знову ввімкнено",
            "titolo": "Раді, що ти залишаєшся",
            "paragrafi": [
                "Автоподовження підписки {piano} знову ввімкнено.",
                "{data} ми подовжимо її за {importo} зі знижкою за автоподовження. До цього дня ти можеш вимкнути "
                "його в профілі будь-коли.",
            ],
            "pulsante": "Керувати підпискою",
        },
        "es": {
            "oggetto": "La renovación automática vuelve a estar activa",
            "titolo": "Nos alegra que sigas",
            "paragrafi": [
                "La renovación automática de tu suscripción {piano} vuelve a estar activa.",
                "El {data} la renovaremos por {importo}, con el descuento de renovación automática. Puedes "
                "desactivarla desde tu perfil cuando quieras antes de esa fecha.",
            ],
            "pulsante": "Gestionar la suscripción",
        },
    },
    # -- il promemoria della prova --------------------------------------------------------------------------------
    "promemoria_prova": {
        "en": {
            "oggetto": "Your free trial ends on {data}",
            "titolo": "Your free trial ends in {giorni} days",
            "paragrafi": [
                "Your free {piano} trial ends on {data}.",
                "If you do nothing, on that day it becomes a yearly {piano} subscription for {importo} a year — "
                "{sconto}% off, for as long as you stay. Your card will be charged then, not before.",
                "Don't want to continue? Turn off renewal in your profile before {data}: nothing will be charged, and "
                "your trial runs until the end.",
            ],
            "pulsante": "Review your trial",
        },
        "it": {
            "oggetto": "La tua prova gratuita finisce il {data}",
            "titolo": "La tua prova gratuita finisce fra {giorni} giorni",
            "paragrafi": [
                "La tua prova gratuita di {piano} finisce il {data}.",
                "Se non fai nulla, quel giorno diventa un abbonamento annuale {piano} a {importo} all'anno — con il "
                "{sconto}% di sconto, per sempre finché resti. La carta verrà addebitata allora, non prima.",
                "Non vuoi continuare? Disattiva il rinnovo dal profilo prima del {data}: non ti verrà addebitato nulla "
                "e la prova continua fino alla fine.",
            ],
            "pulsante": "Rivedi la tua prova",
        },
        "hu": {
            "oggetto": "Az ingyenes próbaidőd {data} napon lejár",
            "titolo": "Az ingyenes próbaidőd {giorni} nap múlva lejár",
            "paragrafi": [
                "A(z) {piano} ingyenes próbaidőd {data} napon lejár.",
                "Ha nem teszel semmit, aznap éves {piano} előfizetéssé válik, évi {importo} áron — {sconto}% "
                "kedvezménnyel, amíg velünk maradsz. A kártyádat akkor terheljük, előtte nem.",
                "Nem szeretnéd folytatni? Kapcsold ki a megújítást a profilodban {data} előtt: semmit sem terhelünk, "
                "és a próbaidő a végéig tart.",
            ],
            "pulsante": "Próbaidő megtekintése",
        },
        "ru": {
            "oggetto": "Твой бесплатный пробный период заканчивается {data}",
            "titolo": "Пробный период скоро закончится",
            "paragrafi": [
                "Твой бесплатный пробный период {piano} заканчивается {data}.",
                "Если ничего не делать, в этот день он станет годовой подпиской {piano} за {importo} в год — со "
                "скидкой {sconto}% навсегда, пока ты с нами. Карта будет списана тогда, не раньше.",
                "Не хочешь продолжать? Отключи продление в профиле до {data}: ничего не спишется, а пробный период "
                "продлится до конца.",
            ],
            "pulsante": "Посмотреть пробный период",
        },
        "uk": {
            "oggetto": "Твій безкоштовний пробний період закінчується {data}",
            "titolo": "Пробний період скоро закінчиться",
            "paragrafi": [
                "Твій безкоштовний пробний період {piano} закінчується {data}.",
                "Якщо нічого не робити, цього дня він стане річною підпискою {piano} за {importo} на рік — зі знижкою "
                "{sconto}% назавжди, поки ти з нами. Картку буде списано тоді, не раніше.",
                "Не хочеш продовжувати? Вимкни подовження в профілі до {data}: нічого не спишеться, а пробний період "
                "триватиме до кінця.",
            ],
            "pulsante": "Переглянути пробний період",
        },
        "es": {
            "oggetto": "Tu prueba gratuita termina el {data}",
            "titolo": "Tu prueba gratuita termina en {giorni} días",
            "paragrafi": [
                "Tu prueba gratuita de {piano} termina el {data}.",
                "Si no haces nada, ese día se convierte en una suscripción anual {piano} por {importo} al año — con un "
                "{sconto}% de descuento para siempre, mientras sigas con nosotros. Tu tarjeta se cargará entonces, no "
                "antes.",
                "¿No quieres continuar? Desactiva la renovación en tu perfil antes del {data}: no se cobrará nada y la "
                "prueba sigue hasta el final.",
            ],
            "pulsante": "Revisar tu prueba",
        },
    },
    # -- il pagamento non riuscito ---------------------------------------------------------------------------------
    "pagamento_fallito": {
        "en": {
            "oggetto": "We couldn't renew your subscription",
            "titolo": "Your payment didn't go through",
            "paragrafi": [
                "We tried to renew your {piano} subscription, but the payment of {importo} didn't go through.",
                "Nothing is lost: for the next {giorni} days (until {data}) your included readings stay active, and "
                "we will try the payment again automatically.",
                "You can settle the same invoice right now from the link below. Paying it stops the automatic retries, "
                "so you will never be charged twice.",
            ],
            "pulsante": "Fix your payment",
        },
        "it": {
            "oggetto": "Non siamo riusciti a rinnovare il tuo abbonamento",
            "titolo": "Il pagamento non è andato a buon fine",
            "paragrafi": [
                "Abbiamo provato a rinnovare il tuo abbonamento {piano}, ma il pagamento di {importo} non è andato a "
                "buon fine.",
                "Non hai perso niente: per i prossimi {giorni} giorni (fino al {data}) le letture comprese restano "
                "attive, e riproveremo il pagamento da soli.",
                "Puoi saldare subito la stessa fattura dal link qui sotto. Pagarla ferma i nuovi tentativi: non ti "
                "verrà mai addebitato due volte.",
            ],
            "pulsante": "Sistema il pagamento",
        },
        "hu": {
            "oggetto": "Nem sikerült megújítani az előfizetésedet",
            "titolo": "A fizetés nem sikerült",
            "paragrafi": [
                "Megpróbáltuk megújítani a(z) {piano} előfizetésedet, de a(z) {importo} összegű fizetés nem sikerült.",
                "Semmi sem veszett el: a következő {giorni} napban ({data} napig) a benne foglalt olvasásaid aktívak "
                "maradnak, és automatikusan újra megpróbáljuk a fizetést.",
                "Az alábbi linken most rögtön kifizetheted ugyanazt a számlát. Ezzel leállnak az automatikus "
                "próbálkozások, így soha nem fizetsz kétszer.",
            ],
            "pulsante": "Fizetés rendezése",
        },
        "ru": {
            "oggetto": "Не удалось продлить твою подписку",
            "titolo": "Платёж не прошёл",
            "paragrafi": [
                "Мы попытались продлить твою подписку {piano}, но платёж на {importo} не прошёл.",
                "Ничего не потеряно: до {data} включённые расклады остаются активными, а "
                "мы автоматически попробуем списать оплату ещё раз.",
                "Ты можешь оплатить тот же счёт прямо сейчас по ссылке ниже. Оплата останавливает автоматические "
                "попытки, поэтому дважды с тебя не спишут никогда.",
            ],
            "pulsante": "Исправить оплату",
        },
        "uk": {
            "oggetto": "Не вдалося подовжити твою підписку",
            "titolo": "Платіж не пройшов",
            "paragrafi": [
                "Ми спробували подовжити твою підписку {piano}, але платіж на {importo} не пройшов.",
                "Нічого не втрачено: до {data} включені розклади залишаються активними, а "
                "ми автоматично спробуємо списати оплату ще раз.",
                "Ти можеш оплатити той самий рахунок просто зараз за посиланням нижче. Оплата зупиняє автоматичні "
                "спроби, тож двічі з тебе не спишуть ніколи.",
            ],
            "pulsante": "Виправити оплату",
        },
        "es": {
            "oggetto": "No hemos podido renovar tu suscripción",
            "titolo": "El pago no se ha completado",
            "paragrafi": [
                "Intentamos renovar tu suscripción {piano}, pero el pago de {importo} no se ha completado.",
                "No has perdido nada: durante los próximos {giorni} días (hasta el {data}) tus lecturas incluidas "
                "siguen activas, y volveremos a intentar el cobro automáticamente.",
                "Puedes pagar la misma factura ahora mismo desde el enlace de abajo. Al pagarla se detienen los "
                "reintentos automáticos: nunca se te cobrará dos veces.",
            ],
            "pulsante": "Arreglar el pago",
        },
    },
    # -- i solleciti (giorno 3 e giorno 6) -------------------------------------------------------------------------
    "sollecito": {
        "en": {
            "oggetto": "Reminder: your subscription payment is still pending",
            "titolo": "{giorni} days left to fix your payment",
            "paragrafi": [
                "The payment for your {piano} subscription is still pending.",
                "Your included readings stay active until {data}. After that they will be paused until the invoice "
                "is paid.",
                "Paying the open invoice takes a minute and stops the automatic retries: you will not be charged "
                "twice.",
            ],
            "pulsante": "Fix your payment",
        },
        "it": {
            "oggetto": "Promemoria: il pagamento del tuo abbonamento è ancora in sospeso",
            "titolo": "Restano {giorni} giorni per sistemare il pagamento",
            "paragrafi": [
                "Il pagamento del tuo abbonamento {piano} è ancora in sospeso.",
                "Le letture comprese restano attive fino al {data}. Dopo saranno sospese finché la fattura non sarà "
                "pagata.",
                "Pagare la fattura aperta richiede un minuto e ferma i nuovi tentativi: non ti verrà addebitato due "
                "volte.",
            ],
            "pulsante": "Sistema il pagamento",
        },
        "hu": {
            "oggetto": "Emlékeztető: az előfizetésed fizetése még függőben van",
            "titolo": "Még {giorni} napod van rendezni a fizetést",
            "paragrafi": [
                "A(z) {piano} előfizetésed fizetése még függőben van.",
                "A benne foglalt olvasásaid {data} napig aktívak maradnak. Utána szünetelnek, amíg a számlát ki nem "
                "fizeted.",
                "A nyitott számla kifizetése egy perc, és leállítja az újabb próbálkozásokat: nem fizetsz kétszer.",
            ],
            "pulsante": "Fizetés rendezése",
        },
        "ru": {
            "oggetto": "Напоминание: оплата подписки всё ещё не прошла",
            "titolo": "Исправь оплату до {data}",
            "paragrafi": [
                "Оплата твоей подписки {piano} всё ещё не прошла.",
                "Включённые расклады остаются активными до {data}. После этого они будут приостановлены, пока счёт "
                "не будет оплачен.",
                "Оплатить открытый счёт — дело минуты, и это останавливает повторные попытки: дважды с тебя не "
                "спишут.",
            ],
            "pulsante": "Исправить оплату",
        },
        "uk": {
            "oggetto": "Нагадування: оплата підписки досі не пройшла",
            "titolo": "Виправ оплату до {data}",
            "paragrafi": [
                "Оплата твоєї підписки {piano} досі не пройшла.",
                "Включені розклади залишаються активними до {data}. Після цього їх буде призупинено, доки рахунок не "
                "буде оплачено.",
                "Оплатити відкритий рахунок — справа хвилини, і це зупиняє повторні спроби: двічі з тебе не спишуть.",
            ],
            "pulsante": "Виправити оплату",
        },
        "es": {
            "oggetto": "Recordatorio: el pago de tu suscripción sigue pendiente",
            "titolo": "Te quedan {giorni} días para arreglar el pago",
            "paragrafi": [
                "El pago de tu suscripción {piano} sigue pendiente.",
                "Tus lecturas incluidas siguen activas hasta el {data}. Después se pausarán hasta que se pague la "
                "factura.",
                "Pagar la factura abierta lleva un minuto y detiene los reintentos: no se te cobrará dos veces.",
            ],
            "pulsante": "Arreglar el pago",
        },
    },
    # -- la sospensione --------------------------------------------------------------------------------------------
    "sospensione": {
        "en": {
            "oggetto": "Your subscription is paused",
            "titolo": "Your included readings are paused",
            "paragrafi": [
                "We didn't receive the payment for your {piano} subscription within the {giorni} days of grace, so "
                "your included readings are now paused.",
                "Your credits, your readings and your story are all still here. Pay the open invoice from your "
                "profile and everything starts again at once.",
            ],
            "pulsante": "Reactivate your subscription",
        },
        "it": {
            "oggetto": "Il tuo abbonamento è sospeso",
            "titolo": "Le letture comprese sono sospese",
            "paragrafi": [
                "Il pagamento del tuo abbonamento {piano} non è arrivato entro i {giorni} giorni di tolleranza: le "
                "letture comprese sono sospese.",
                "I tuoi crediti, le tue letture e la tua storia restano tutti qui. Salda la fattura aperta dal profilo "
                "e tutto riparte subito.",
            ],
            "pulsante": "Riattiva l'abbonamento",
        },
        "hu": {
            "oggetto": "Az előfizetésed szünetel",
            "titolo": "A benne foglalt olvasásaid szünetelnek",
            "paragrafi": [
                "A(z) {piano} előfizetésed díja nem érkezett meg a {giorni} napos türelmi időn belül, ezért a benne "
                "foglalt olvasások szünetelnek.",
                "A krediteid, az olvasásaid és a történeted mind megvannak. Fizesd ki a nyitott számlát a profilodban, "
                "és minden azonnal újraindul.",
            ],
            "pulsante": "Előfizetés újraindítása",
        },
        "ru": {
            "oggetto": "Твоя подписка приостановлена",
            "titolo": "Включённые расклады приостановлены",
            "paragrafi": [
                "Оплата подписки {piano} не поступила в течение {giorni} дней льготного периода, поэтому включённые "
                "расклады приостановлены.",
                "Твои кредиты, расклады и твоя история никуда не делись. Оплати открытый счёт в профиле — и всё "
                "сразу заработает снова.",
            ],
            "pulsante": "Возобновить подписку",
        },
        "uk": {
            "oggetto": "Твою підписку призупинено",
            "titolo": "Включені розклади призупинено",
            "paragrafi": [
                "Оплата підписки {piano} не надійшла протягом {giorni} днів пільгового періоду, тому включені розклади "
                "призупинено.",
                "Твої кредити, розклади й твоя історія нікуди не зникли. Оплати відкритий рахунок у профілі — і все "
                "одразу запрацює знову.",
            ],
            "pulsante": "Відновити підписку",
        },
        "es": {
            "oggetto": "Tu suscripción está en pausa",
            "titolo": "Tus lecturas incluidas están en pausa",
            "paragrafi": [
                "No recibimos el pago de tu suscripción {piano} dentro de los {giorni} días de margen, así que tus "
                "lecturas incluidas están en pausa.",
                "Tus créditos, tus lecturas y tu historia siguen aquí. Paga la factura abierta desde tu perfil y todo "
                "vuelve a funcionar al instante.",
            ],
            "pulsante": "Reactivar la suscripción",
        },
    },
    # -- il rinnovo avvenuto ---------------------------------------------------------------------------------------
    "rinnovo_avvenuto": {
        "en": {
            "oggetto": "Your subscription has been renewed",
            "titolo": "Thank you for staying",
            "paragrafi": [
                "Your {piano} subscription has been renewed: {importo}, valid until {data}.",
                "Your included readings are ready. You can manage renewal from your profile at any time.",
            ],
            "pulsante": "Open your profile",
        },
        "it": {
            "oggetto": "Il tuo abbonamento è stato rinnovato",
            "titolo": "Grazie di restare con noi",
            "paragrafi": [
                "Il tuo abbonamento {piano} è stato rinnovato: {importo}, valido fino al {data}.",
                "Le tue letture comprese ti aspettano. Puoi gestire il rinnovo dal profilo in qualunque momento.",
            ],
            "pulsante": "Apri il profilo",
        },
        "hu": {
            "oggetto": "Az előfizetésed megújult",
            "titolo": "Köszönjük, hogy velünk maradsz",
            "paragrafi": [
                "A(z) {piano} előfizetésed megújult: {importo}, érvényes {data} napig.",
                "A benne foglalt olvasásaid várnak. A megújítást bármikor kezelheted a profilodban.",
            ],
            "pulsante": "Profil megnyitása",
        },
        "ru": {
            "oggetto": "Твоя подписка продлена",
            "titolo": "Спасибо, что ты с нами",
            "paragrafi": [
                "Твоя подписка {piano} продлена: {importo}, действует до {data}.",
                "Включённые расклады ждут тебя. Управлять продлением можно в профиле в любой момент.",
            ],
            "pulsante": "Открыть профиль",
        },
        "uk": {
            "oggetto": "Твою підписку подовжено",
            "titolo": "Дякуємо, що ти з нами",
            "paragrafi": [
                "Твою підписку {piano} подовжено: {importo}, діє до {data}.",
                "Включені розклади чекають на тебе. Керувати подовженням можна в профілі будь-коли.",
            ],
            "pulsante": "Відкрити профіль",
        },
        "es": {
            "oggetto": "Tu suscripción se ha renovado",
            "titolo": "Gracias por seguir con nosotros",
            "paragrafi": [
                "Tu suscripción {piano} se ha renovado: {importo}, válida hasta el {data}.",
                "Tus lecturas incluidas te esperan. Puedes gestionar la renovación desde tu perfil cuando quieras.",
            ],
            "pulsante": "Abrir tu perfil",
        },
    },
}

#: I mesi, per scrivere le date come le scrive una persona (in russo e ucraino al genitivo: «3 октября»).
MESI: Dict[str, List[str]] = {
    "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
           "November", "December"],
    "it": ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre",
           "novembre", "dicembre"],
    "hu": ["január", "február", "március", "április", "május", "június", "július", "augusztus", "szeptember",
           "október", "november", "december"],
    "ru": ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября",
           "ноября", "декабря"],
    "uk": ["січня", "лютого", "березня", "квітня", "травня", "червня", "липня", "серпня", "вересня", "жовтня",
           "листопада", "грудня"],
    "es": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
           "noviembre", "diciembre"],
}
