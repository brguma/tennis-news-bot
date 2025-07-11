#!/usr/bin/env python3
"""
Script para testar e verificar a atualização dos rankings
Execute: python test_rankings.py
"""

from tennis_bot import fetch_atp_rankings, fetch_wta_rankings, update_rankings, load_current_players
import json
from datetime import datetime

def test_atp_rankings():
    """Testa busca dos rankings ATP"""
    print("🔄 Testando busca ATP rankings...")
    
    players = fetch_atp_rankings(50)  # Testa com top 50
    
    if players:
        print(f"✅ ATP: {len(players)} jogadores encontrados")
        print("🔝 Top 10 ATP:")
        for i, player in enumerate(players[:10], 1):
            print(f"  {i:2d}. {player}")
        return True
    else:
        print("❌ Falha ao buscar rankings ATP")
        return False

def test_wta_rankings():
    """Testa busca dos rankings WTA"""
    print("\n🔄 Testando busca WTA rankings...")
    
    players = fetch_wta_rankings(50)  # Testa com top 50
    
    if players:
        print(f"✅ WTA: {len(players)} jogadoras encontradas")
        print("🔝 Top 10 WTA:")
        for i, player in enumerate(players[:10], 1):
            print(f"  {i:2d}. {player}")
        return True
    else:
        print("❌ Falha ao buscar rankings WTA")
        return False

def test_full_update():
    """Testa atualização completa"""
    print("\n🔄 Testando atualização completa dos rankings...")
    
    players = update_rankings()
    
    if len(players) > 400:
        print(f"✅ Atualização completa: {len(players)} jogadores")
        
        # Verifica arquivo salvo
        try:
            with open('current_rankings.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            atp_count = len(data.get('atp_top_250', []))
            wta_count = len(data.get('wta_top_250', []))
            last_updated = data.get('last_updated', 'N/A')
            
            print(f"📊 Rankings salvos:")
            print(f"  👨 ATP: {atp_count} jogadores")
            print(f"  👩 WTA: {wta_count} jogadoras")
            print(f"  📅 Última atualização: {last_updated}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao verificar arquivo salvo: {e}")
            return False
    else:
        print(f"⚠️ Poucos jogadores encontrados: {len(players)}")
        return False

def show_current_rankings():
    """Mostra rankings atualmente carregados"""
    print("\n📊 Rankings atualmente carregados:")
    
    players = load_current_players()
    print(f"📈 Total de jogadores: {len(players)}")
    
    # Tenta mostrar estatísticas do arquivo
    try:
        with open('current_rankings.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        atp_players = data.get('atp_top_250', [])
        wta_players = data.get('wta_top_250', [])
        last_updated = data.get('last_updated', '')
        
        if last_updated:
            update_date = datetime.fromisoformat(last_updated)
            days_old = (datetime.now() - update_date).days
            
            print(f"👨 ATP: {len(atp_players)} jogadores")
            print(f"👩 WTA: {len(wta_players)} jogadoras")
            print(f"📅 Atualizado em: {update_date.strftime('%d/%m/%Y às %H:%M')}")
            print(f"⏰ Idade: {days_old} dias")
            
            if days_old > 7:
                print("⚠️ Rankings estão antigos (>7 dias)")
            else:
                print("✅ Rankings estão atualizados")
        
        print(f"\n🔝 Primeiros 10 jogadores:")
        for i, player in enumerate(players[:10], 1):
            print(f"  {i:2d}. {player}")
    
    except FileNotFoundError:
        print("❌ Arquivo de rankings não encontrado")
        print("🔄 Execute a atualização primeiro")
    except Exception as e:
        print(f"❌ Erro ao ler rankings: {e}")

def main():
    """Função principal de testes"""
    print("🎾 TESTE DOS RANKINGS DE TÊNIS")
    print("=" * 40)
    
    # Mostra rankings atuais
    show_current_rankings()
    
    print("\n" + "=" * 40)
    print("🔍 TESTANDO BUSCA DOS RANKINGS")
    
    # Testa buscas individuais
    atp_ok = test_atp_rankings()
    wta_ok = test_wta_rankings()
    
    # Testa atualização completa se as individuais funcionaram
    if atp_ok and wta_ok:
        full_ok = test_full_update()
        
        if full_ok:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            print("✅ O sistema de rankings está funcionando perfeitamente")
        else:
            print("\n⚠️ Teste de atualização completa falhou")
    else:
        print("\n❌ Falha nos testes básicos")
        print("🔧 Verifique sua conexão e tente novamente")
    
    print("\n" + "=" * 40)

if __name__ == "__main__":
    main()#!/usr/bin/env python3
"""
Script para testar e verificar a atualização dos rankings
Execute: python test_rankings.py
"""

from tennis_bot import fetch_atp_rankings, fetch_wta_rankings, update_rankings, load_current_players
import json
from datetime import datetime

def test_atp_rankings():
    """Testa busca dos rankings ATP"""
    print("🔄 Testando busca ATP rankings...")
    
    players = fetch_atp_rankings(50)  # Testa com top 50
    
    if players:
        print(f"✅ ATP: {len(players)} jogadores encontrados")
        print("🔝 Top 10 ATP:")
        for i, player in enumerate(players[:10], 1):
            print(f"  {i:2d}. {player}")
        return True
    else:
        print("❌ Falha ao buscar rankings ATP")
        return False

def test_wta_rankings():
    """Testa busca dos rankings WTA"""
    print("\n🔄 Testando busca WTA rankings...")
    
    players = fetch_wta_rankings(50)  # Testa com top 50
    
    if players:
        print(f"✅ WTA: {len(players)} jogadoras encontradas")
        print("🔝 Top 10 WTA:")
        for i, player in enumerate(players[:10], 1):
            print(f"  {i:2d}. {player}")
        return True
    else:
        print("❌ Falha ao buscar rankings WTA")
        return False

def test_full_update():
    """Testa atualização completa"""
    print("\n🔄 Testando atualização completa dos rankings...")
    
    players = update_rankings()
    
    if len(players) > 400:
        print(f"✅ Atualização completa: {len(players)} jogadores")
        
        # Verifica arquivo salvo
        try:
            with open('current_rankings.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            atp_count = len(data.get('atp_top_250', []))
            wta_count = len(data.get('wta_top_250', []))
            last_updated = data.get('last_updated', 'N/A')
            
            print(f"📊 Rankings salvos:")
            print(f"  👨 ATP: {atp_count} jogadores")
            print(f"  👩 WTA: {wta_count} jogadoras")
            print(f"  📅 Última atualização: {last_updated}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao verificar arquivo salvo: {e}")
            return False
    else:
        print(f"⚠️ Poucos jogadores encontrados: {len(players)}")
        return False

def show_current_rankings():
    """Mostra rankings atualmente carregados"""
    print("\n📊 Rankings atualmente carregados:")
    
    players = load_current_players()
    print(f"📈 Total de jogadores: {len(players)}")
    
    # Tenta mostrar estatísticas do arquivo
    try:
        with open('current_rankings.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        atp_players = data.get('atp_top_250', [])
        wta_players = data.get('wta_top_250', [])
        last_updated = data.get('last_updated', '')
        
        if last_updated:
            update_date = datetime.fromisoformat(last_updated)
            days_old = (datetime.now() - update_date).days
            
            print(f"👨 ATP: {len(atp_players)} jogadores")
            print(f"👩 WTA: {len(wta_players)} jogadoras")
            print(f"📅 Atualizado em: {update_date.strftime('%d/%m/%Y às %H:%M')}")
            print(f"⏰ Idade: {days_old} dias")
            
            if days_old > 7:
                print("⚠️ Rankings estão antigos (>7 dias)")
            else:
                print("✅ Rankings estão atualizados")
        
        print(f"\n🔝 Primeiros 10 jogadores:")
        for i, player in enumerate(players[:10], 1):
            print(f"  {i:2d}. {player}")
    
    except FileNotFoundError:
        print("❌ Arquivo de rankings não encontrado")
        print("🔄 Execute a atualização primeiro")
    except Exception as e:
        print(f"❌ Erro ao ler rankings: {e}")

def main():
    """Função principal de testes"""
    print("🎾 TESTE DOS RANKINGS DE TÊNIS")
    print("=" * 40)
    
    # Mostra rankings atuais
    show_current_rankings()
    
    print("\n" + "=" * 40)
    print("🔍 TESTANDO BUSCA DOS RANKINGS")
    
    # Testa buscas individuais
    atp_ok = test_atp_rankings()
    wta_ok = test_wta_rankings()
    
    # Testa atualização completa se as individuais funcionaram
    if atp_ok and wta_ok:
        full_ok = test_full_update()
        
        if full_ok:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            print("✅ O sistema de rankings está funcionando perfeitamente")
        else:
            print("\n⚠️ Teste de atualização completa falhou")
    else:
        print("\n❌ Falha nos testes básicos")
        print("🔧 Verifique sua conexão e tente novamente")
    
    print("\n" + "=" * 40)

if __name__ == "__main__":
    main()
