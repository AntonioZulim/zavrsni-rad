# zavrsni-rad

## Parametri

### action space
- zasad svaka faza svoju akciju (N-S i E-W)
- mozda kasnije dodati i dijagonale ili svaka strana svoju akciju
- alternativa: relativne akcije keep i switch

### observation space
- vrijeme cekanja na semaforu
- velicina reda na semaforu
- trenutna faza
- koliko dugo traje trenutna faza

### reward function
- vrijeme cekanja na semaforu
- velicina reda na semaforu
- mozda dati blagu kaznu za promjenu faze kako ne bi divljao na pocetku

## TODO

- [] ~~bolji graf~~
- [x] popraviti reward
- [x] riješiti učitavanje ruta
- [] usporedba s fiksnim rasporedom
- [] izvrtiti više situacija
- [] isprobati više algoritama i usporediti