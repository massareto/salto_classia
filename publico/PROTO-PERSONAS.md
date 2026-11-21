# Renderização das proto-personas

Crie `proto-personas/perfis.json` na pasta do negócio. Use estas chaves em ambos os idiomas e escreva os valores no idioma do pedido.

```json
{
  "language": "pt",
  "profiles": [
    {
      "name": "Nome fictício",
      "segment": "Descrição curta do perfil",
      "evidence": "mixed",
      "portrait": "retratos/01.png",
      "scene": {
        "setting": "Balcão de uma loja de bairro",
        "background": "Estantes de mercadorias",
        "in_hand": "Caderno de contas",
        "clothing": "Camisa de algodão e avental"
      },
      "behaviors": ["Hábito, crença ou valor que pesa na decisão"],
      "demographics": {
        "age": "35–44 anos",
        "sex": "Feminino",
        "occupation": "Dona de papelaria",
        "education": "Graduação em Administração",
        "children": "Sim, um filho",
        "marital_status": "Casada",
        "location": "Campinas, Brasil"
      },
      "goals": ["Resultado que quer atingir"],
      "needs": ["O que precisa para avançar"]
    }
  ]
}
```

Inclua exatamente três objetos em `profiles` e use `pt` ou `en` em `language`. Defina `evidence` como `mixed` quando houver achados e hipóteses combinados ou `hypothesis` quando o perfil ainda for uma hipótese. Complete os sete campos demográficos para cada personagem composto. Use dados da pesquisa ou estimativas baseadas no recorte mais comparável. Se só for possível fazer uma escolha ilustrativa, registre-a com transparência no relatório. Os valores no exemplo são apenas fictícios. Ao atualizar uma ficha antiga, revise os campos vazios e as pendências antes de renderizar. Preserve os achados e a justificativa das estimativas no relatório. Use de cinco a sete tópicos breves em `behaviors` e de quatro a seis em cada uma das listas `goals` e `needs`, conforme a evidência. Prefira frases de até seis palavras, uma informação por tópico. Sinalize a hipótese no tópico em que aparece e guarde os links e recortes no relatório Markdown.

Feche primeiro o perfil escrito e só então gere três retratos em estilo de fotografia editorial hiper-realista com a ferramenta de imagem disponível. Use formato horizontal próximo de 2:1 para preencher o quadrante. Faça um retrato ambiental da cintura para cima, com textura natural de pele, luz realista, rosto, mãos e roupa visíveis. Mantenha o personagem e o objeto longe das bordas para preservar ambos no recorte. Use a faixa etária, a apresentação de gênero e o contexto profissional do perfil ao compor a fotografia. Mostre o local concreto, detalhes reconhecíveis ao fundo e o personagem segurando um objeto pertinente à rotina. Use roupa compatível com a situação. Registre em `scene` os quatro elementos que realmente aparecem na foto, em frases curtas no idioma da ficha. Mantenha nomes e marcas fora da imagem. Desenhos, avatares gráficos, caricaturas e renderizações 3D ficam fora da entrega. Use personagens fictícios e trate a foto como representação do perfil. A fotografia representa o perfil construído pela pesquisa e pelas estimativas. Confira se o resultado está coerente antes de montar a ficha. Salve as três fotos em uma pasta de trabalho e informe o caminho relativo ao JSON em `portrait`. O renderizador usa o arquivo informado. Se a geração de foto estiver indisponível, informe o que falta antes de apresentar o material como completo.

Execute o comando abaixo da pasta do negócio, substituindo o caminho pelo local onde extraiu o ZIP.

```sh
python3 /caminho/do/zip/scripts/render.py proto-personas/perfis.json
```

Se Pillow ainda não estiver disponível, instale-o em um ambiente virtual do projeto e use o Python desse ambiente para executar o renderizador. O script gera `01.png`, `02.png` e `03.png` ao lado do JSON. Encurte o texto se o renderizador indicar que algum quadrante ficou sem espaço. Abra os PNGs e faça os ajustes antes de entregar.
