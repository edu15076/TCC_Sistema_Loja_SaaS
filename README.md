# TCC_Sistema_Loja_SaaS

<details>

<summary><h2>Indice</h2></summary>

  - [Configuração de Ambiente](#configuração-do-ambiente)
  - [Commits](#commits)

</details>

## Configuração do ambiente

Por padrão, todas as orientações nessa seção partem do ponto de vista que o terminal já está no diretório `TCC_Sistema_Loja_SaaS/src`.

Para rodar o projeto, é recomendavel o uso de um ambiente virtual python, para isso, rode:

``` bash
python -m venv venv
```

após isso é necessário ativar o ambiente, no **windows**, use:

```bash
env\Scripts\activate.bat
```
e no **linux** use:

```bash
source env/bin/activate
```
Feito a criação e ativação do ambiente virtual, instale as dependencias com:

```bash
pip install -r requirements.txt
```
Após concluir esses processos, crie um arquivo com as variáveis chamado `.env`. O conteudo desse arquivo deve seguir seguinte formato:

```dotenv
DATABASE_NAME="<db>"
DATABASE_USER="<user>"
DATABASE_PASSWORD="<password>"
DATABASE_HOST="<host>"
DATABASE_PORT="<port>"
```
Note que os valores entre colchetes angulares devem ser substituidos pelos respectivos paramentros de comfiguração do banco de dados na sua máquina.

**IMPORTANTE:** O sistema está configurado a usar Postgresql.

## Commits

Para facilitar desenvolvimento, use mensagens descritivas nos commits, no inicio da mensagem use commits semanticos segundo o quadro abaixo:

<table>
  <thead>
    <tr>
      <th>Tipo do commit</th>
      <th>Codigo</th>
    </tr>
  </thead>
 <tbody>
    <tr>
      <td>Alterações de revisão de código</td>
      <td>👌 <code>:ok_hand: style</code></td>
    </tr>
    <tr>
      <td>Bugfix</td>
      <td>🐛 <code>:bug: fix:</code></td>
    </tr>
    <tr>
      <td>Configuração</td>
      <td>🔧 <code>:wrench: chore:</code></td>
    </tr>
    <tr>
      <td>Documentação</td>
      <td>📚 <code>:books: docs:</code></td>
    </tr>
    <tr>
      <td>Em progresso</td>
      <td>🚧 <code>:construction:</code></td>
    </tr>
    <tr>
      <td>Estilização de interface</td>
      <td>💄 <code>:lipstick: feat</code></td>
    </tr>
    <tr>
      <td>Mover/Renomear</td>
      <td>🚚 <code>:truck: chore:</code></td>
    </tr>
    <tr>
      <td>Novo recurso</td>
      <td>✨ <code>:sparkles: feat:</code></td>
    </tr>
    <tr>
      <td>Performance</td>
      <td>⚡ <code>:zap: perf:</code></td>
    </tr>
    <tr>
        <td>Refatoração</td>
        <td>♻️ <code>:recycle: refactor:</code></td>
    </tr>
    <tr>
      <td>Removendo um arquivo</td>
      <td>🔥 <code>:fire:</code></td>
    </tr>
    <tr>
      <td>Revertendo mudanças</td>
      <td>💥 <code>:boom: fix:</code></td>
    </tr>
    <tr>
      <td>Tag de versão</td>
      <td>🔖 <code>:bookmark:</code></td>
    </tr>
    <tr>
      <td>Testes</td>
      <td>🧪 <code>:test_tube: test:</code></td>
    </tr>
    <tr>
      <td>Tratamento de erros</td>
      <td>🥅 <code>:goal_net: fix:</code></td>
    </tr>
    <tr>
      <td>Mundança no Makefile e arquvos de build</td>
      <td>🔨 <code>:hammer: build:</code></td>
    </tr>
    <tr>
      <td>Dados</td>
      <td>🗃️ <code>:card_file_box: raw:</code></td>
    </tr>
  </tbody>
</table>

As palavras chaves são as seguintes:
- `feat`- Commits do tipo feat indicam que seu trecho de código está incluindo um **novo recurso** (se relaciona com o MINOR do versionamento semântico).

- `fix` - Commits do tipo fix indicam que seu trecho de código commitado está **solucionando um problema** (bug fix), (se relaciona com o PATCH do versionamento semântico).

- `docs` - Commits do tipo docs indicam que houveram **mudanças na documentação**, como por exemplo no Readme do seu repositório. (Não inclui alterações em código).

- `test` - Commits do tipo test são utilizados quando são realizadas **alterações em testes**, seja criando, alterando ou excluindo testes unitários. (Não inclui alterações em código)

- `build` - Commits do tipo build são utilizados quando são realizadas modificações em **arquivos de build e dependências**.

- `perf` - Commits do tipo perf servem para identificar quaisquer alterações de código que estejam relacionadas a **performance**.

- `style` - Commits do tipo style indicam que houveram alterações referentes a **formatações de código**, semicolons, trailing spaces, lint... (Não inclui alterações em código).

- `refactor` - Commits do tipo refactor referem-se a mudanças devido a **refatorações que não alterem sua funcionalidade**, como por exemplo, uma alteração no formato como é processada determinada parte da tela, mas que manteve a mesma funcionalidade, ou melhorias de performance devido a um code review.

- `chore` - Commits do tipo chore indicam **atualizações de tarefas** de build, configurações de administrador, pacotes... como por exemplo adicionar um pacote no gitignore. (Não inclui alterações em código)

- `raw` - Commits to tipo raw indicam mudanças relacionadas a arquivos de configurações, dados, features, parametros.

Exemplos:
- <code>git commit -m ":books: docs: Atualização do README"</code>
- <code>git commit -m ":construction: trabalhando na classe de interpretador"</code>
- <code>git commit -m ":sparkles: feat: interpretador terminado"</code>
