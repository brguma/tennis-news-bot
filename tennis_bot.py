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

# URLs dos feeds RSS e sites para monitorar
NEWS_SOURCES = {
    'ATP Tour': 'https://www.atptour.com/en/news/rss-feed',
    'WTA Tour': 'https://www.wtatennis.com/rss',
    'Tennis.com': 'https://www.tennis.com/rss-feeds/',
    'ESPN Tennis': 'https://www.espn.com/espn/rss/tennis/news'
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
        
        # Método mais simples primeiro
        try:
            api_url = "https://www.atptour.com/en/rankings/singles"
            response = requests.get(api_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Busca links de jogadores
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
        
        # Método simples apenas
        try:
            url = "https://www.wtatennis.com/rankings/singles"
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Busca qualquer link que pareça nome de jogadora
            all_links = soup.find_all('a')
            
            for link in all_links:
                if len(players) >= max_players or (time.time() - start_time) > timeout_seconds:
                    break
                    
                name = link.get_text().strip()
                # Filtro básico para nomes (duas palavras, sem números)
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
    
    # Busca rankings atuais com timeout
    atp_players = fetch_atp_rankings(250, timeout_seconds=20)
    wta_players = fetch_wta_rankings(250, timeout_seconds=20)
    
    # NOVA LÓGICA: Usa o que conseguiu + backup para completar
    final_atp = atp_players if len(atp_players) > 20 else BACKUP_PLAYERS_MEN
    final_wta = wta_players if len(wta_players) > 20 else BACKUP_PLAYERS_WOMEN
    
    # Remove duplicatas
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
    
    # Salva os rankings
    with open('current_rankings.json', 'w', encoding='utf-8') as f:
        json.dump(rankings_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Rankings finalizados: {len(final_atp)} homens + {len(final_wta)} mulheres")
    print(f"📊 ATP: {rankings_data['atp_source']} | WTA: {rankings_data['wta_source']}")
    return final_atp + final_wta

def load_current_players():
    """Carrega a lista atual de jogadores"""
    try:
        # Tenta carregar rankings salvos
        with open('current_rankings.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Verifica se os rankings não estão muito antigos (máximo 2 semanas)
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
        
        # Atualiza a cada 7 dias
        return days_since_update >= 7
    
    except:
        return True  # Se não conseguir ler, força atualização

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
        print(f"🔍 Buscando notícias de {source_name}...")
        feed = feedparser.parse(url)
        
        news_items = []
        for entry in feed.entries[:10]:
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

def fetch_web_news(players):
    """Busca notícias diretamente de sites"""
    news_items = []
    
    try:
        print("🔍 Buscando notícias do ATP Tour...")
        response = requests.get('https://www.atptour.com/en/news', timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        articles = soup.find_all('article', class_='news-item', limit=5)
        for article in articles:
            title_elem = article.find('h3') or article.find('h2')
            link_elem = article.find('a')
            
            if title_elem and link_elem:
                title = title_elem.get_text().strip()
                link = 'https://www.atptour.com' + link_elem.get('href', '')
                
                mentioned_players = check_player_mentioned(title, players)
                if mentioned_players:
                    news_items.append({
                        'title': title,
                        'description': title,
                        'link': link,
                        'source': 'ATP Tour',
                        'players': mentioned_players,
                        'date': datetime.now().strftime('%Y-%m-%d')
                    })
        
        print(f"✅ ATP Site: {len(news_items)} notícias relevantes")
    
    except Exception as e:
        print(f"❌ Erro ao buscar ATP Tour: {e}")
    
    return news_items

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
    
    message = f"""🎾 <b>{news_item['source']}</b>

<b>{news_item['title']}</b>

👤 <i>{players_text}</i>

📖 {summary}

🔗 <a href="{news_item['link']}">Ler matéria completa</a>"""
    
    return message

def main():
    """Função principal"""
    print("🚀 Iniciando Tennis News Bot...")
    
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Tokens do Telegram não configurados!")
        return
    
    # Atualiza rankings se necessário (SEM POSSIBILIDADE DE LOOP)
    if should_update_rankings():
        current_players = update_rankings()
    else:
        current_players = load_current_players()
    
    print(f"📊 Monitorando {len(current_players)} jogadores")
    
    # Carrega notícias já enviadas
    sent_news = load_sent_news()
    
    all_news = []
    
    # Busca em feeds RSS
    for source_name, url in NEWS_SOURCES.items():
        news_items = fetch_rss_news(url, source_name, current_players)
        all_news.extend(news_items)
    
    # Busca diretamente em sites
    web_news = fetch_web_news(current_players)
    all_news.extend(web_news)
    
    # Remove duplicatas e filtra notícias já enviadas
    new_news = []
    for news in all_news:
        if not is_duplicate(news, sent_news) and not is_duplicate(news, new_news):
            new_news.append(news)
    
    print(f"📰 Encontradas {len(new_news)} notícias novas")
    
    if not new_news:
        today = datetime.now().strftime('%d/%m/%Y')
        message = f"🎾 <b>Tênis News - {today}</b>\n\n📭 Nenhuma notícia nova sobre os top players hoje.\n\n🔄 Próxima busca amanhã às 8h!"
        send_telegram_message(message)
        print("📭 Nenhuma notícia nova encontrada")
        return
    
    # Envia mensagem de cabeçalho
    today = datetime.now().strftime('%d/%m/%Y')
    header = f"🎾 <b>Tênis News - {today}</b>\n\n📊 {len(new_news)} notícias encontradas:"
    send_telegram_message(header)
    
    # Envia cada notícia
    for i, news in enumerate(new_news[:10], 1):
        message = format_message(news)
        send_telegram_message(message)
        sent_news.append(news)
        
        if i < len(new_news):
            time.sleep(2)
    
    # Salva notícias enviadas
    save_sent_news(sent_news)
    
    print(f"✅ Processo concluído! {len(new_news)} notícias enviadas.")

if __name__ == "__main__":
    main()
