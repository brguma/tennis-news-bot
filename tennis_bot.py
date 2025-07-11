import os
import requests
import feedparser
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta
import re

# Configurações do Telegram
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Lista de backup caso a busca automática falhe
BACKUP_PLAYERS_MEN = [
    "Novak Djokovic", "Carlos Alcaraz", "Daniil Medvedev", "Jannik Sinner",
    "Andrey Rublev", "Stefanos Tsitsipas", "Rafael Nadal", "Holger Rune",
    "Casper Ruud", "Taylor Fritz", "Alex de Minaur", "Tommy Paul",
    "Alexander Zverev", "Grigor Dimitrov", "Ben Shelton", "Frances Tiafoe",
    "Sebastian Korda", "Hubert Hurkacz", "Lorenzo Musetti", "Karen Khachanov",
    "Felix Auger-Aliassime", "Cameron Norrie", "Nicolas Jarry", "Ugo Humbert",
    "Arthur Fils", "Jan-Lennard Struff", "Matteo Berrettini", "Tomas Machac",
    "Sebastian Baez", "Alejandro Tabilo", "Flavio Cobolli", "Francisco Cerundolo",
    "Adrian Mannarino", "Mariano Navone", "Jordan Thompson", "Giovanni Mpetshi Perricard",
    "Alexei Popyrin", "Brandon Nakashima", "Jiri Lehecka", "Pedro Martinez",
    "Nuno Borges", "Matteo Arnaldi", "Luciano Darderi", "Alexander Bublik",
    "Zhang Yifan", "Tallon Griekspoor", "Arthur Rinderknech", "Roberto Carballes Baena",
    "Christopher O'Connell", "Pavel Kotov"
]

BACKUP_PLAYERS_WOMEN = [
    "Aryna Sabalenka", "Iga Swiatek", "Coco Gauff", "Elena Rybakina",
    "Jessica Pegula", "Qinwen Zheng", "Barbora Krejcikova", "Emma Navarro",
    "Daria Kasatkina", "Danielle Collins", "Paula Badosa", "Diana Shnaider",
    "Donna Vekic", "Madison Keys", "Anna Kalinskaya", "Marta Kostyuk",
    "Jelena Ostapenko", "Beatriz Haddad Maia", "Mirra Andreeva", "Katie Boulter",
    "Magdalena Frech", "Liudmila Samsonova", "Victoria Azarenka", "Yulia Putintseva",
    "Jasmine Paolini", "Caroline Wozniacki", "Elise Mertens", "Linda Noskova",
    "Anastasia Pavlyuchenkova", "Leylah Fernandez", "Clara Tauson", "Maria Sakkari",
    "Petra Kvitova", "Sloane Stephens", "Caroline Garcia", "Amanda Anisimova",
    "Elina Svitolina", "Veronika Kudermetova", "Ekaterina Alexandrova", "Ons Jabeur",
    "Karolina Muchova", "Anastasia Potapova", "Naomi Osaka", "Sorana Cirstea",
    "Peyton Stearns", "Anna Blinkova", "Lulu Sun", "Kaia Kanepi",
    "Xinyu Wang", "Cristina Bucsa"
]

# URLs dos feeds RSS expandidos
RSS_NEWS_SOURCES = {
    'ATP Tour': 'https://www.atptour.com/en/news/rss-feed',
    'WTA Tour': 'https://www.wtatennis.com/rss',
    'Tennis.com': 'https://www.tennis.com/rss-feeds/',
    'ESPN Tennis': 'https://www.espn.com/espn/rss/tennis/news',
    'Eurosport Tennis': 'https://www.eurosport.com/rss/tennis/',
    'Tennis Channel': 'https://www.tennischannel.com/rss',
    'ITF': 'https://www.itftennis.com/en/news/rss/',
    'UOL Esporte Tênis': 'https://esporte.uol.com.br/tenis/rss.xml',
    'Bola Amarela': 'https://bolamarela.com.br/feed/',
    'Bola Amarela RSS': 'https://bolamarela.com.br/rss/',
    'Globo Esporte Tênis 🇧🇷': 'https://ge.globo.com/tenis/rss.xml',
    'Olé Tenis 🇦🇷': 'https://www.ole.com.ar/tenis/rss.xml',
    'Marca Tenis 🇪🇸': 'https://www.marca.com/rss/tenis.xml',
    'L\'Équipe Tennis 🇫🇷': 'https://www.lequipe.fr/rss/actu_rss_Tennis.xml',
    'Tennis World USA': 'https://www.tennisworldusa.org/rss.xml',
    'Tennis World Italy': 'https://www.tennisworld.it/rss.xml'
}

# Sites para scraping direto
WEB_SCRAPING_SOURCES = [
    {
        'name': 'ATP Tour News',
        'url': 'https://www.atptour.com/en/news',
        'selectors': {
            'articles': 'article.news-item, .news-listing-item, .article-item',
            'title': 'h3, h2, .news-title, .article-title',
            'link': 'a',
            'description': '.news-summary, .article-summary, p'
        }
    },
    {
        'name': 'WTA News',
        'url': 'https://www.wtatennis.com/news',
        'selectors': {
            'articles': '.news-item, .article-card, .news-card',
            'title': 'h3, h2, .title, .news-title',
            'link': 'a',
            'description': '.summary, .excerpt, p'
        }
    },
    {
        'name': 'Tennis.com News',
        'url': 'https://www.tennis.com/news',
        'selectors': {
            'articles': '.article-item, .news-item, article',
            'title': 'h3, h2, .title',
            'link': 'a',
            'description': '.excerpt, .summary, p'
        }
    },
    {
        'name': 'Bola Amarela 🇧🇷',
        'url': 'https://bolamarela.com.br/',
        'selectors': {
            'articles': 'article, .post, .entry, .news-item, .article-item',
            'title': 'h1, h2, h3, .entry-title, .post-title, .article-title',
            'link': 'a',
            'description': '.entry-content, .post-content, .excerpt, .summary, p'
        }
    },
    {
        'name': 'Globo Esporte Tênis 🇧🇷',
        'url': 'https://ge.globo.com/tenis/',
        'selectors': {
            'articles': '.feed-post, .hui-premium, article, .bastian-feed-item',
            'title': 'h2, .feed-post-link, .hui-premium__title, .feed-post-body-title',
            'link': 'a',
            'description': '.feed-post-body-resumo, .hui-premium__chapeu, p'
        }
    },
    {
        'name': 'Marca Tenis 🇪🇸',
        'url': 'https://www.marca.com/tenis.html',
        'selectors': {
            'articles': 'article, .articulo, .story',
            'title': 'h2, h3, .titulo',
            'link': 'a',
            'description': '.entradilla, .excerpt, p'
        }
    },
    {
        'name': 'L\'Équipe Tennis 🇫🇷',
        'url': 'https://www.lequipe.fr/Tennis/',
        'selectors': {
            'articles': 'article, .Article, .ArticleListItem',
            'title': 'h2, h3, .Article__title, .ArticleListItem__title',
            'link': 'a',
            'description': '.Article__excerpt, .ArticleListItem__excerpt, p'
        }
    },
    {
        'name': 'Olé Tenis 🇦🇷',
        'url': 'https://www.ole.com.ar/tenis/',
        'selectors': {
            'articles': 'article, .nota, .story-item',
            'title': 'h2, h3, .nota-title, .story-title',
            'link': 'a',
            'description': '.nota-excerpt, .story-excerpt, p'
        }
    }
]

# Jornalistas e fontes do Twitter (usando métodos alternativos)
TWITTER_SOURCES = {
    'José Morgado': {
        'username': 'josemorgado',
        'rss_alternative': 'https://nitter.net/josemorgado/rss',  # Usando Nitter como alternativa
        'backup_url': 'https://twitter.com/josemorgado'
    },
    'Tennis TV': {
        'username': 'TennisTV',
        'rss_alternative': 'https://nitter.net/TennisTV/rss',
        'backup_url': 'https://twitter.com/TennisTV'
    },
    'Ben Rothenberg': {
        'username': 'BenRothenberg',
        'rss_alternative': 'https://nitter.net/BenRothenberg/rss',
        'backup_url': 'https://twitter.com/BenRothenberg'
    },
    'Christopher Clarey': {
        'username': 'christophclarey',
        'rss_alternative': 'https://nitter.net/christophclarey/rss',
        'backup_url': 'https://twitter.com/christophclarey'
    }
}

def fetch_atp_rankings(max_players=250, timeout_seconds=30):
    """Busca rankings atuais do ATP com timeout"""
    print(f"🔄 Buscando top {max_players} ATP rankings...")
    start_time = time.time()
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        players = []
        
        try:
            api_url = "https://www.atptour.com/en/rankings/singles"
            response = requests.get(api_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            player_links = soup.find_all('a', href=lambda x: x and '/en/players/' in x)
            
            for link in player_links:
                if len(players) >= max_players or (time.time() - start_time) > timeout_seconds:
                    break
                    
                name = link.get_text().strip()
                if name and len(name.split()) >= 2 and name not in players:
                    players.append(name)
        except Exception as e:
            print(f"  ⚠️ Método principal ATP falhou: {e}")
        
        print(f"✅ ATP: {len(players)} jogadores encontrados")
        return players[:max_players]
    
    except Exception as e:
        print(f"❌ Erro ao buscar ATP rankings: {e}")
        return []

def fetch_wta_rankings(max_players=250, timeout_seconds=30):
    """Busca rankings atuais do WTA com timeout"""
    print(f"🔄 Buscando top {max_players} WTA rankings...")
    start_time = time.time()
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        players = []
        
        try:
            url = "https://www.wtatennis.com/rankings/singles"
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            all_links = soup.find_all('a')
            
            for link in all_links:
                if len(players) >= max_players or (time.time() - start_time) > timeout_seconds:
                    break
                    
                name = link.get_text().strip()
                if (name and 
                    len(name.split()) >= 2 and 
                    not any(char.isdigit() for char in name) and
                    len(name) > 5 and len(name) < 40 and
                    name not in players):
                    players.append(name)
                    
        except Exception as e:
            print(f"  ⚠️ WTA scraping falhou: {e}")
        
        print(f"✅ WTA: {len(players)} jogadoras encontradas")
        return players[:max_players]
    
    except Exception as e:
        print(f"❌ Erro ao buscar WTA rankings: {e}")
        return []

def update_rankings():
    """Atualiza os rankings dos jogadores (SEM LOOP)"""
    print("🔄 Atualizando rankings...")
    
    atp_players = fetch_atp_rankings(250, timeout_seconds=20)
    wta_players = fetch_wta_rankings(250, timeout_seconds=20)
    
    final_atp = atp_players if len(atp_players) > 20 else BACKUP_PLAYERS_MEN
    final_wta = wta_players if len(wta_players) > 20 else BACKUP_PLAYERS_WOMEN
    
    final_atp = list(dict.fromkeys(final_atp))[:250]
    final_wta = list(dict.fromkeys(final_wta))[:250]
    
    rankings_data = {
        'atp_top_250': final_atp,
        'wta_top_250': final_wta,
        'last_updated': datetime.now().isoformat(),
        'total_players': len(final_atp) + len(final_wta),
        'atp_source': 'live' if len(atp_players) > 20 else 'backup',
        'wta_source': 'live' if len(wta_players) > 20 else 'backup'
    }
    
    with open('current_rankings.json', 'w', encoding='utf-8') as f:
        json.dump(rankings_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Rankings finalizados: {len(final_atp)} homens + {len(final_wta)} mulheres")
    print(f"📊 ATP: {rankings_data['atp_source']} | WTA: {rankings_data['wta_source']}")
    return final_atp + final_wta

def load_current_players():
    """Carrega a lista atual de jogadores"""
    try:
        with open('current_rankings.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        last_updated = datetime.fromisoformat(data['last_updated'])
        if (datetime.now() - last_updated).days <= 14:
            players = data.get('atp_top_250', []) + data.get('wta_top_250', [])
            print(f"📊 Usando rankings salvos: {len(players)} jogadores (atualizado em {last_updated.strftime('%d/%m/%Y')})")
            return players
        else:
            print("⚠️ Rankings salvos estão antigos, forçando atualização...")
            return update_rankings()
    
    except FileNotFoundError:
        print("📋 Primeira execução - buscando rankings...")
        return update_rankings()
    
    except Exception as e:
        print(f"❌ Erro ao carregar rankings: {e}")
        print("📋 Usando lista de backup...")
        return BACKUP_PLAYERS_MEN + BACKUP_PLAYERS_WOMEN

def should_update_rankings():
    """Verifica se precisa atualizar os rankings"""
    try:
        with open('current_rankings.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        last_updated = datetime.fromisoformat(data['last_updated'])
        days_since_update = (datetime.now() - last_updated).days
        
        return days_since_update >= 7
    
    except:
        return True

def send_telegram_message(message):
    """Envia mensagem para o grupo do Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': False
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"✅ Mensagem enviada: {message[:50]}...")
        else:
            print(f"❌ Erro ao enviar mensagem: {response.text}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

def clean_text(text):
    """Limpa e formata o texto"""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def create_summary(content, max_chars=250):
    """Cria um resumo da notícia"""
    content = clean_text(content)
    
    if len(content) <= max_chars:
        return content
    
    sentences = content.split('.')
    summary = ""
    
    for sentence in sentences:
        if len(summary + sentence + ".") <= max_chars - 3:
            summary += sentence + "."
        else:
            break
    
    if not summary:
        words = content.split()
        summary = ""
        for word in words:
            if len(summary + word + " ") <= max_chars - 3:
                summary += word + " "
            else:
                break
        summary = summary.strip() + "..."
    
    return summary

def check_player_mentioned(text, players):
    """Verifica se algum jogador da lista é mencionado no texto"""
    text_lower = text.lower()
    mentioned_players = []
    
    for player in players:
        if player.lower() in text_lower:
            mentioned_players.append(player)
            continue
        
        name_parts = player.split()
        if len(name_parts) > 1:
            surname = name_parts[-1].lower()
            if len(surname) > 3 and surname in text_lower:
                mentioned_players.append(player)
    
    return mentioned_players

def fetch_rss_news(url, source_name, players):
    """Busca notícias de feeds RSS"""
    try:
        print(f"🔍 Buscando notícias RSS de {source_name}...")
        feed = feedparser.parse(url)
        
        news_items = []
        for entry in feed.entries[:15]:  # Aumentei para 15 por fonte
            title = entry.title if hasattr(entry, 'title') else ''
            description = entry.summary if hasattr(entry, 'summary') else ''
            link = entry.link if hasattr(entry, 'link') else ''
            
            full_text = f"{title} {description}"
            mentioned_players = check_player_mentioned(full_text, players)
            
            if mentioned_players:
                news_items.append({
                    'title': title,
                    'description': description,
                    'link': link,
                    'source': source_name,
                    'players': mentioned_players,
                    'date': datetime.now().strftime('%Y-%m-%d')
                })
        
        print(f"✅ {source_name}: {len(news_items)} notícias relevantes")
        return news_items
    
    except Exception as e:
        print(f"❌ Erro ao buscar {source_name}: {e}")
        return []

def fetch_website_news(site_config, players):
    """Busca notícias diretamente de sites usando configuração flexível"""
    try:
        print(f"🔍 Buscando notícias de {site_config['name']}...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(site_config['url'], headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        news_items = []
        articles = soup.select(site_config['selectors']['articles'])[:10]
        
        for article in articles:
            try:
                # Busca título
                title_elem = article.select_one(site_config['selectors']['title'])
                title = title_elem.get_text().strip() if title_elem else ''
                
                # Busca link
                link_elem = article.select_one(site_config['selectors']['link'])
                if link_elem:
                    link = link_elem.get('href', '')
                    if link and not link.startswith('http'):
                        base_url = '/'.join(site_config['url'].split('/')[:3])
                        link = base_url + (link if link.startswith('/') else '/' + link)
                else:
                    link = ''
                
                # Busca descrição
                desc_elem = article.select_one(site_config['selectors']['description'])
                description = desc_elem.get_text().strip() if desc_elem else title
                
                if title and link:
                    full_text = f"{title} {description}"
                    mentioned_players = check_player_mentioned(full_text, players)
                    
                    if mentioned_players:
                        news_items.append({
                            'title': title,
                            'description': description,
                            'link': link,
                            'source': site_config['name'],
                            'players': mentioned_players,
                            'date': datetime.now().strftime('%Y-%m-%d')
                        })
            
            except Exception as e:
                continue  # Skip artigos com erro
        
        print(f"✅ {site_config['name']}: {len(news_items)} notícias relevantes")
        return news_items
    
    except Exception as e:
        print(f"❌ Erro ao buscar {site_config['name']}: {e}")
        return []

def fetch_twitter_alternative(source_name, config, players):
    """Busca tweets usando alternativas ao Twitter API"""
    try:
        print(f"🔍 Buscando tweets de {source_name}...")
        
        news_items = []
        
        # Tenta usar Nitter RSS como alternativa
        try:
            rss_url = config['rss_alternative']
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries[:5]:  # Só os 5 mais recentes
                title = entry.title if hasattr(entry, 'title') else ''
                description = entry.summary if hasattr(entry, 'summary') else ''
                link = entry.link if hasattr(entry, 'link') else ''
                
                full_text = f"{title} {description}"
                mentioned_players = check_player_mentioned(full_text, players)
                
                if mentioned_players:
                    news_items.append({
                        'title': f"🐦 {title}",
                        'description': description,
                        'link': link,
                        'source': f"Twitter - {source_name}",
                        'players': mentioned_players,
                        'date': datetime.now().strftime('%Y-%m-%d')
                    })
        
        except Exception as e:
            print(f"  ⚠️ RSS do {source_name} falhou: {e}")
        
        print(f"✅ Twitter {source_name}: {len(news_items)} tweets relevantes")
        return news_items
    
    except Exception as e:
        print(f"❌ Erro ao buscar Twitter {source_name}: {e}")
        return []

def load_sent_news():
    """Carrega notícias já enviadas para evitar duplicatas"""
    try:
        with open('sent_news.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_sent_news(sent_news):
    """Salva notícias já enviadas"""
    cutoff_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    filtered_news = [
        news for news in sent_news 
        if news.get('date', '2000-01-01') >= cutoff_date
    ]
    
    with open('sent_news.json', 'w') as f:
        json.dump(filtered_news, f, indent=2)

def is_duplicate(news_item, sent_news):
    """Verifica se a notícia já foi enviada"""
    for sent in sent_news:
        if (sent.get('title') == news_item['title'] or 
            sent.get('link') == news_item['link']):
            return True
    return False

def format_message(news_item):
    """Formata a mensagem para o Telegram"""
    players_text = ", ".join(news_item['players'][:3])
    if len(news_item['players']) > 3:
        players_text += f" e mais {len(news_item['players']) - 3}"
    
    summary = create_summary(news_item['description'])
    
    # Adiciona emoji baseado na fonte
    emoji = "🎾"
    source = news_item['source'].lower()
    
    if "twitter" in source:
        emoji = "🐦"
    elif "instagram" in source:
        emoji = "📸"
    elif "atp" in source:
        emoji = "🏆"
    elif "wta" in source:
        emoji = "👸"
    elif any(br_term in source for br_term in ["bola amarela", "uol", "sportv", "globo"]):
        emoji = "🇧🇷"
    elif any(es_term in source for es_term in ["marca", "spain", "españa"]):
        emoji = "🇪🇸"
    elif any(fr_term in source for fr_term in ["équipe", "lequipe", "france"]):
        emoji = "🇫🇷"
    elif any(ar_term in source for ar_term in ["olé", "ole", "argentina"]):
        emoji = "🇦🇷"
    elif any(eu_term in source for eu_term in ["eurosport", "europa"]):
        emoji = "🇪🇺"
    elif any(us_term in source for us_term in ["espn", "tennis.com", "tennis channel"]):
        emoji = "🇺🇸"
    elif any(it_term in source for it_term in ["italy", "italia"]):
        emoji = "🇮🇹"
    
    message = f"""{emoji} <b>{news_item['source']}</b>

<b>{news_item['title']}</b>

👤 <i>{players_text}</i>

📖 {summary}

🔗 <a href="{news_item['link']}">Ler matéria completa</a>"""
    
    return message

def main():
    """Função principal"""
    print("🚀 Iniciando Tennis News Bot GLOBAL EXPANDIDO...")
    
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Tokens do Telegram não configurados!")
        return
    
    # Atualiza rankings se necessário
    if should_update_rankings():
        current_players = update_rankings()
    else:
        current_players = load_current_players()
    
    print(f"📊 Monitorando {len(current_players)} jogadores")
    
    sent_news = load_sent_news()
    all_news = []
    
    # 1. Busca em feeds RSS (múltiplas fontes)
    print(f"\n📡 Buscando em {len(RSS_NEWS_SOURCES)} feeds RSS globais...")
    for source_name, url in RSS_NEWS_SOURCES.items():
        news_items = fetch_rss_news(url, source_name, current_players)
        all_news.extend(news_items)
    
    # 2. Busca em sites com scraping
    print(f"\n🌐 Buscando em {len(WEB_SCRAPING_SOURCES)} sites oficiais...")
    for site_config in WEB_SCRAPING_SOURCES:
        news_items = fetch_website_news(site_config, current_players)
        all_news.extend(news_items)
    
    # 3. Busca em Twitter (via alternativas)
    print(f"\n🐦 Buscando em {len(TWITTER_SOURCES)} fontes do Twitter/X...")
    for source_name, config in TWITTER_SOURCES.items():
        news_items = fetch_twitter_alternative(source_name, config, current_players)
        all_news.extend(news_items)
    
    # Remove duplicatas e filtra notícias já enviadas
    new_news = []
    for news in all_news:
        if not is_duplicate(news, sent_news) and not is_duplicate(news, new_news):
            new_news.append(news)
    
    print(f"\n📰 RESUMO GLOBAL: {len(all_news)} notícias encontradas, {len(new_news)} novas")
    
    # Estatísticas por país/região
    sources_stats = {}
    for news in new_news:
        source = news['source']
        if '🇧🇷' in source or any(br in source.lower() for br in ['bola amarela', 'uol', 'globo', 'sportv']):
            sources_stats['Brasil 🇧🇷'] = sources_stats.get('Brasil 🇧🇷', 0) + 1
        elif '🇪🇸' in source or 'marca' in source.lower():
            sources_stats['Espanha 🇪🇸'] = sources_stats.get('Espanha 🇪🇸', 0) + 1
        elif '🇫🇷' in source or 'équipe' in source.lower():
            sources_stats['França 🇫🇷'] = sources_stats.get('França 🇫🇷', 0) + 1
        elif '🇦🇷' in source or 'olé' in source.lower():
            sources_stats['Argentina 🇦🇷'] = sources_stats.get('Argentina 🇦🇷', 0) + 1
        elif any(intl in source.lower() for intl in ['atp', 'wta', 'tennis.com', 'espn']):
            sources_stats['Internacional 🌍'] = sources_stats.get('Internacional 🌍', 0) + 1
        else:
            sources_stats['Outras 🎾'] = sources_stats.get('Outras 🎾', 0) + 1
    
    if sources_stats:
        print("📊 Notícias por região:")
        for region, count in sources_stats.items():
            print(f"  {region}: {count} notícias")
    
    if not new_news:
        today = datetime.now().strftime('%d/%m/%Y')
        message = f"🎾 <b>Tênis News Global - {today}</b>\n\n📭 Nenhuma notícia nova sobre os top players hoje.\n\n🌍 Fontes monitoradas: {len(RSS_NEWS_SOURCES) + len(WEB_SCRAPING_SOURCES) + len(TWITTER_SOURCES)} internacionais\n\n🔄 Próxima busca amanhã às 8h!"
        send_telegram_message(message)
        print("📭 Nenhuma notícia nova encontrada")
        return
    
    # Envia mensagem de cabeçalho
    today = datetime.now().strftime('%d/%m/%Y')
    sources_count = len(set(news['source'] for news in new_news))
    total_sources = len(RSS_NEWS_SOURCES) + len(WEB_SCRAPING_SOURCES) + len(TWITTER_SOURCES)
    header = f"🎾 <b>Tênis News Global - {today}</b>\n\n📊 {len(new_news)} notícias de {sources_count} fontes\n🌍 Cobertura: Brasil, Espanha, França, Argentina e internacional"
    send_telegram_message(header)
    
    # Envia cada notícia (máximo 20 por dia para acomodar mais fontes)
    for i, news in enumerate(new_news[:20], 1):
        message = format_message(news)
        send_telegram_message(message)
        sent_news.append(news)
        
        if i < len(new_news):
            time.sleep(3)  # Pausa maior para evitar spam
    
    # Salva notícias enviadas
    save_sent_news(sent_news)
    
    print(f"✅ Processo GLOBAL concluído! {len(new_news[:20])} notícias enviadas de {sources_count} fontes.")
    print(f"🌍 Total de fontes monitoradas: {total_sources} (RSS: {len(RSS_NEWS_SOURCES)}, Sites: {len(WEB_SCRAPING_SOURCES)}, Twitter: {len(TWITTER_SOURCES)})")

if __name__ == "__main__":
    main()
