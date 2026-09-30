/* La biblioteca delle carte e la pagina di una carta. */

import type { carte as Base } from "../en/carte";

export const carte: typeof Base = {
  meta_titolo: "Бібліотека карт Таро Тота",
  meta_descrizione: "78 карт Таро Тота: образи, відповідності та значення — кожна з них є входом до питання.",
  eyebrow: "Бібліотека карт Таро Тота",
  titolo: "Подивися на карту, перш ніж просити її заговорити.",
  intro: "Кожна карта поєднує образ, низку відповідностей і значення на кількох рівнях. Її роль у читанні все одно залежить від позиції, сусідніх карт і твого питання.",
  filtri: { tutte: "Усі", maggiori: "Старші Аркани", bastoni: "Жезли", coppe: "Кубки", spade: "Мечі", dischi: "Диски" } as Record<string, string>,
  filtri_aria: "Фільтрувати карти",
  n_carte: { uno: "1 карта", molti: "Карт: {n}" },

  /* one card */
  carta_eyebrow: "Таро Тота · {arcano}",
  carta_riflessione: "Відправна точка для роздумів",
  carta_domanda: "На що карта «{carta}» просить тебе подивитися?",
  carta_nota: "Значення змінюється залежно від позиції, сусідніх карт і твого питання. Сприймай те, що далі, як мову, а не як вирок.",
  dritta: "Пряма",
  rovesciata: "Перевернута",
  rovesciata_nota: "У традиції Тота перевернуту карту читають через її гідність щодо сусідніх карт; це її тіньовий бік.",
  livelli: { essoterico: "На перший погляд", psicologico: "Усередині тебе", iniziatico: "На шляху", ombra: "Тінь" } as Record<string, string>,
  ambiti_titolo: "У коханні, роботі й дусі",
  ambiti: { amore: "Кохання", lavoro: "Робота", spirito: "Дух" } as Record<string, string>,
  corrispondenze: "Відповідності",
  sentiero: "стежка {n}",
  crowley: "Примітка Кроулі",
  parole: "Ключові слова",
  cta_leggi: "Прочитати цю карту в ритуалі",
  cta_fisica: "Витягни її з власної колоди",
  articoli_su: "З журналу",
  precedente: "Попередня карта",
  successiva: "Наступна карта",
  torna: "Назад до бібліотеки",
  non_trovata: "Цієї карти немає в бібліотеці.",
};
