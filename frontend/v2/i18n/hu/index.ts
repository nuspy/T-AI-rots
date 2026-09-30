/* Magyar: tradotto. */

import type { en } from "../en";
import { blog } from "./blog";
import { carte } from "./carte";
import { comune } from "./comune";
import { condivisa } from "./condivisa";
import { fisica } from "./fisica";
import { giorno } from "./giorno";
import { home } from "./home";
import { lettura } from "./lettura";
import { mazzi } from "./mazzi";
import { negozio } from "./negozio";
import { prezzi } from "./prezzi";
import { privacy } from "./privacy";
import { profilo } from "./profilo";
import { stese } from "./stese";
import { storia } from "./storia";

export const hu: typeof en = { comune, home, lettura, fisica, storia, condivisa, carte, giorno, stese, mazzi, negozio, prezzi, blog, profilo, privacy };
