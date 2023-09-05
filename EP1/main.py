import scrapy

class PokemonSpider(scrapy.Spider):
    name = 'pokemons'
    start_urls = ['https://pokemondb.net/pokedex/all']
    base_url = 'https://pokemondb.net'

    def parse(self, response):
      ### tabela de seletores de CSS
      # table é a tabela inteira
      # #pokedex é o nome da tabela
      # tbody é oq ta dentro da tabela(linhas)
      # tr é cada linha em si
      # se eu usar o comando no inspecionar e voltar a tabela ta certo :)
      # $('table#pokedex > tbody > tr') <= assim
        tabela_pokedex = "table#pokedex > tbody > tr"
      
        linhas = response.css(tabela_pokedex)
        #linha = linhas[1]
        #coluna_href = linha.css("td:nth-child(2) > a::attr(href)")
        #yield response.follow(coluna_href.get(), self.parser_pokemon)
        for linha in linhas:
            #coluna_nome = linha.css("td:nth-child(2) > a::text")
            #coluna_id = linha.css("td:nth-child(1) > span.infocard-cell-data::text")
            #yield {'id': coluna_id.get(), 'nome': coluna_nome.get()}
            coluna_href = linha.css("td:nth-child(2) > a::attr(href)")
            yield response.follow(coluna_href.get(), self.parse_pokemon)

    def parse_pokemon(self, response):
        # Selectors de CSS que serão utilizados para extrair as informações
        id_selector = ".vitals-table > tbody > tr:nth-child(1) > td > strong::text"
        name_selector = "#main > h1::text"
        weight_selector = ".vitals-table > tbody > tr:nth-child(5) > td::text"
        height_selector = ".vitals-table > tbody > tr:nth-child(4) > td::text"
        types_selector = ".grid-row > div:nth-child(2) > table > tbody > tr:nth-child(2) > td > a:nth-child(1)::text"
        types_selector2 = ".grid-row > div:nth-child(2) > table > tbody > tr:nth-child(2) > td > a:nth-child(2)::text"
        ability_selector = ".vitals-table > tbody > tr:nth-child(6) > td > span > a::attr(href)"
        evolutions_selector = ".infocard-list-evo > div.infocard"

        # Obtendo informações sobre o pokemon
        id = response.css(id_selector)
        name = response.css(name_selector)
        weight = response.css(weight_selector)
        height = response.css(height_selector)
        types = response.css(types_selector)
        types2 = response.css(types_selector2)
        url = response.request.url

        # Obtendo informações sobre evoluções
        evolutions = []
        # Para cada evolução, obtemos o id, nome e url
        for evolucoes in response.css(evolutions_selector):
            idEvolucao = evolucoes.css("span > small::text").get()
            nomeEvolucao = evolucoes.css("span:nth-child(2) > a::text").get()
            urlEvolucao = evolucoes.css("span:nth-child(2) > a::attr(href)").get()

            evolucao = {
                'IdEvolucao': idEvolucao if idEvolucao else None,
                'NomeEvolucao': nomeEvolucao,
                'UrlEvolucao': f"{self.base_url}{urlEvolucao}" if urlEvolucao else None
            }
            evolutions.append(evolucao)
        
        # Criando um dicionário com as informações do pokemon
        linha = {
            'id': int(id.get()),
            'name': name.get().strip(),
            'weight': weight.get(),
            'height': height.get(),
            'types': types.get(),
            'types2': types2.get(),
            'url': url,  
            'abilities': [],
            'evolutions': evolutions
        }

        # Obtendo informações sobre habilidades
        css_result = response.css(ability_selector).getall()

        # Para cada habilidade, obtemos o nome e url
        for href_ability in css_result:
            request = scrapy.Request(f"{self.base_url}{href_ability}", callback=self.parse_ability)
            request.meta['linha'] = linha
            yield request

    # Função para obter informações sobre habilidades
    def parse_ability(self, response):
        # Obtendo informações sobre habilidades
        ability_info = response.css("#main > div > div > p::text").getall()
        ability_name = response.css("#main > h1::text").get().strip()

        # Obtendo informações sobre o pokemon
        # Utilizamos o meta para obter a linha que foi passada como parâmetro
        # na função parse_pokemon
        linha = response.meta['linha']

        # Adicionando a habilidade na lista de habilidades do pokemon
        linha['abilities'].append({'name': ability_name, 'text': ' '.join(ability_info).strip(), 'url': response.request.url})
        yield linha

