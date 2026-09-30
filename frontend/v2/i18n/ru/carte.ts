/* La biblioteca delle carte e la pagina di una carta. */

import type { carte as Base } from "../en/carte";

export const carte: typeof Base = {
  meta_titolo: "Библиотека карт Таро Тота",
  meta_descrizione: "78 карт Таро Тота: образы, соответствия и значения — каждая как вход в вопрос.",
  eyebrow: "Библиотека карт Таро Тота",
  titolo: "Посмотри на карту, прежде чем просить её заговорить.",
  intro: "Каждая карта соединяет образ, ряд соответствий и значения на нескольких уровнях. Но её роль в раскладе всё равно зависит от позиции, соседних карт и твоего вопроса.",
  filtri: { tutte: "Все", maggiori: "Старшие арканы", bastoni: "Жезлы", coppe: "Чаши", spade: "Мечи", dischi: "Диски" } as Record<string, string>,
  filtri_aria: "Фильтр карт",
  n_carte: { uno: "1 карта", molti: "Карт: {n}" },

  carta_eyebrow: "Таро Тота · {arcano}",
  carta_riflessione: "Отправная точка для размышления",
  carta_domanda: "На что просит тебя взглянуть карта «{carta}»?",
  carta_nota: "Значение меняется вместе с позицией, соседними картами и твоим вопросом. Воспринимай то, что ниже, как язык, а не как приговор.",
  dritta: "Прямое положение",
  rovesciata: "Перевёрнутое положение",
  rovesciata_nota: "В традиции Тота перевёрнутую карту читают через её достоинство по отношению к соседним картам; это её теневая сторона.",
  livelli: { essoterico: "На первый взгляд", psicologico: "Внутри тебя", iniziatico: "На пути", ombra: "Тень" } as Record<string, string>,
  ambiti_titolo: "В любви, работе и духе",
  ambiti: { amore: "Любовь", lavoro: "Работа", spirito: "Дух" } as Record<string, string>,
  corrispondenze: "Соответствия",
  sentiero: "путь {n}",
  crowley: "Заметка Кроули",
  parole: "Ключевые слова",
  cta_leggi: "Прочитать эту карту в ритуале",
  cta_fisica: "Вытянуть её из своей колоды",
  articoli_su: "Из журнала",
  precedente: "Предыдущая карта",
  successiva: "Следующая карта",
  torna: "Назад в библиотеку",
  non_trovata: "Этой карты нет в библиотеке.",
};
