---
name: banca-de-avaliadores
description: Banca de 7 avaliadores que tenta reprovar o currículo do usuário para uma vaga e depois reescreve o currículo corrigindo os erros. Use quando o usuário pedir para revisar, avaliar, melhorar ou reescrever um currículo/CV, ou testar o currículo contra uma vaga.
---

# Banca de Avaliadores

Responda sempre em português.

## Entrada
Peça o que faltar antes de começar:
- o currículo (texto ou PDF);
- a descrição da vaga.

Avise que não precisa enviar dados pessoais que o usuário não queira compartilhar (CPF, endereço completo).

## 1. Banca
Rode cada avaliador separado, sem um ver a nota do outro. Se houver subagentes disponíveis, use um por avaliador.

1. **Filtro automático (ATS):** o que faria o currículo ser descartado antes de uma pessoa ler: formato difícil de ler, palavras-chave da vaga que faltam, seções confusas, datas sem padrão.
2. **Gerente da vaga:** chamaria para entrevista? Sim ou não, explicado em 3 linhas.
3. a 7. **Cinco leitores**, cada um lendo sozinho: o futuro chefe, outro candidato à mesma vaga, o dono da empresa, um recrutador que só tem 30 segundos e um especialista da área. Cada um dá nota de 0 a 10 e aponta os 3 piores problemas.

## 2. Lista de erros
Junte tudo numa lista única, do erro mais grave ao menos grave.

## 3. Reescrita
Reescreva o currículo inteiro corrigindo cada erro, em uma página só.
- Não invente experiência, número, curso ou resultado que não está no original.
- Onde faltar um dado, escreva `[COMPLETAR: o que falta]`.
- Comece cada item com verbo de ação e mostre o resultado com número quando o usuário tiver o número.
- Use as palavras-chave da vaga só onde forem verdade.

## 4. Fechamento
- Mostre uma tabela com o que mudou e por quê.
- Faça a banca avaliar de novo a versão nova, com as novas notas.
- Lembre que a banca aponta erros e reescreve, mas a decisão de chamar para entrevista é de quem contrata.
