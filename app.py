# app.py - Jogo Ciberbatalha em Python (Flask) - Arquivo Único

from flask import Flask, render_template_string, request, session, redirect, url_for
import os

# ====================================================================
# I. TEMPLATE HTML (FRONTEND) - MUDADO PARA O TOPO
# ====================================================================

# O HTML é armazenado como uma string multilinha para ser renderizada pelo Flask
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Ciberbatalha – Simulação de Cartas</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f9; }
        .container { max-width: 900px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        h1 { text-align: center; color: #333; }
        .placar { display: flex; justify-content: space-around; margin-bottom: 20px; padding: 15px; background: #e0f7fa; border-radius: 6px; }
        .placar div { text-align: center; font-size: 1.2em; font-weight: bold; }
        .red-score { color: #e53935; }
        .blue-score { color: #1e88e5; }
        .form-area { display: flex; justify-content: space-between; gap: 20px; }
        .team-select { flex: 1; padding: 15px; border-radius: 6px; }
        #red-team-select { background-color: #ffebee; border: 1px solid #e53935; }
        #blue-team-select { background-color: #e3f2fd; border: 1px solid #1e88e5; }
        select { width: 100%; padding: 10px; margin-top: 5px; border-radius: 4px; border: 1px solid #ccc; }
        .btn-group { margin-top: 20px; text-align: center; }
        button, .reset-btn { padding: 10px 20px; color: white; border: none; border-radius: 4px; cursor: pointer; display: inline-block; margin: 5px; }
        .play-btn { background-color: #4caf50; }
        .play-btn:hover { background-color: #43a047; }
        .reset-btn { background-color: #f44336; text-decoration: none; line-height: 1.5; }
        .reset-btn:hover { background-color: #d32f2f; }
        h2 { border-bottom: 2px solid #ccc; padding-bottom: 5px; margin-top: 30px; }
        .historico { margin-top: 30px; }
        .historico table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        .historico th, .historico td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .historico th { background-color: #f2f2f2; }
        .message { padding: 10px; margin-bottom: 15px; border-radius: 4px; background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba; text-align: center; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚔️ Ciberbatalha – Simulação de Cartas</h1>

        <div class="placar">
            <div>Rodada Atual: {{ rodada }}</div>
            <div class="red-score">Placar Red Team: {{ "%0.1f" | format(placar_red) }}</div>
            <div class="blue-score">Placar Blue Team: {{ "%0.1f" | format(placar_blue) }}</div>
        </div>

        {% if session.get('mensagem') %}
            <div class="message">{{ session.pop('mensagem') }}</div>
        {% endif %}

        <form method="POST" action="{{ url_for('jogar') }}">
            <h2>Jogar Rodada</h2>
            <div class="form-area">
                <div class="team-select" id="red-team-select">
                    <h3>🔴 Red Team (Ataque)</h3>
                    <select name="ataque" required>
                        <option value="">Selecione o Ataque</option>
                        {% for key, value in red_cartas.items() %}
                            <option value="{{ key }}">{{ value }}</option>
                        {% endfor %}
                    </select>
                </div>

                <div class="team-select" id="blue-team-select">
                    <h3>🔵 Blue Team (Defesa)</h3>
                    <select name="defesa" required>
                        <option value="">Selecione a Defesa</option>
                        {% for key, value in blue_cartas.items() %}
                            <option value="{{ key }}">{{ value }}</option>
                        {% endfor %}
                    </select>
                </div>
            </div>
            <div class="btn-group">
                <button type="submit" class="play-btn">Executar Rodada</button>
                <a href="{{ url_for('reset') }}" class="reset-btn">Resetar Jogo</a>
            </div>
        </form>

        <div class="historico">
            <h2>Histórico de Rodadas</h2>
            {% if historico %}
                <table>
                    <thead>
                        <tr>
                            <th>Rodada</th>
                            <th>Ataque (Red)</th>
                            <th>Defesa (Blue)</th>
                            <th>Resultado</th>
                            <th>Pts Red</th>
                            <th>Pts Blue</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for jogada in historico | reverse %}
                            <tr>
                                <td>{{ jogada.rodada }}</td>
                                <td>{{ jogada.ataque }}</td>
                                <td>{{ jogada.defesa }}</td>
                                <td>{{ jogada.resultado }}</td>
                                <td>{{ "%0.1f" | format(jogada.pontos_red) }}</td>
                                <td>{{ "%0.1f" | format(jogada.pontos_blue) }}</td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <p>Nenhuma rodada jogada ainda.</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

# ====================================================================
# II. REGRAS E LÓGICA DO JOGO
# ====================================================================

RED_TEAM_CARTAS = {
    'phishing': 'Phishing',
    'forca_bruta': 'Força Bruta',
    'escaneamento_portas': 'Escaneamento de Portas',
    'ataque_ddos': 'Ataque DDoS',
    'injecao_sql': 'Injeção SQL',
    'malware': 'Malware',
    'ransomware': 'Ransomware',
    'spoofing': 'Spoofing',
    'sniffing_rede': 'Sniffing de Rede',
    'engenharia_social': 'Engenharia Social'
}

BLUE_TEAM_CARTAS = {
    'firewall': 'Firewall',
    'antivirus': 'Antivírus',
    'mfa': 'Autenticação Multifator (MFA)',
    'criptografia': 'Criptografia de Dados',
    'backup': 'Backup Diário',
    'treinamento': 'Treinamento de Usuários',
    'monitoramento_logs': 'Monitoramento de Logs',
    'atualizacoes_patches': 'Atualizações e Patches',
    'segmentacao_rede': 'Segmentação de Rede',
    'senhas_fortes': 'Política de Senhas Fortes'
}

# 🛡️ Lógica de Combate: Mapeia o Ataque (Red) para sua Defesa EFICAZ (Blue)
LOGICA_COMBATE = {
    'phishing': 'treinamento',
    'forca_bruta': 'senhas_fortes',
    'escaneamento_portas': 'firewall',
    'ataque_ddos': 'firewall',
    'injecao_sql': 'atualizacoes_patches',
    'malware': 'antivirus',
    'ransomware': 'backup',
    'spoofing': 'mfa',
    'sniffing_rede': 'criptografia',
    'engenharia_social': 'treinamento'
}


def calcular_pontuacao(ataque, defesa):
    """
    Calcula a pontuação da rodada. Retorna (pontos_red, pontos_blue, resultado_texto).
    """
    ataque_nome = RED_TEAM_CARTAS.get(ataque, "Desconhecido")
    defesa_nome = BLUE_TEAM_CARTAS.get(defesa, "Desconhecida")
    defesa_ideal = LOGICA_COMBATE.get(ataque)

    if defesa == defesa_ideal:
        # 100% Defesa Bem-Sucedida (Ideal)
        return (0, 1, f"DEFESA BEM-SUCEDIDA! O '{defesa_nome}' bloqueou o '{ataque_nome}'.")

    # Casos Críticos / Defesa Ineficaz
    if ataque == 'ransomware' and defesa != 'backup':
        return (1, 0, f"ATAQUE BEM-SUCEDIDO. O '{ataque_nome}' criptografou os arquivos! Blue Team sem Backup.")

    # Casos de Defesa Parcial (Exemplo Personalizado)
    if ataque == 'forca_bruta' and defesa == 'antivirus':
        return (0.5, 0.5, f"DEFESA PARCIAL. O '{defesa_nome}' dificultou o ataque, mas não o bloqueou totalmente.")

    # Padrão: Defesa Ineficaz (Ataque Vence)
    return (1, 0, f"ATAQUE BEM-SUCEDIDO. O '{ataque_nome}' explorou a falha do '{defesa_nome}'.")


# ====================================================================
# III. CONFIGURAÇÃO E ROTAS DO FLASK
# ====================================================================

app = Flask(__name__)
# Chave secreta obrigatória para usar sessions (armazenar placar e histórico)
app.secret_key = os.environ.get('SECRET_KEY', 'cib3rbatalha_s3cr3t_k3y_123')


def inicializar_jogo():
    """Garante que as variáveis de sessão estejam definidas."""
    if 'placar_red' not in session:
        session['placar_red'] = 0.0
        session['placar_blue'] = 0.0
        session['rodada'] = 1
        session['historico'] = []


@app.route('/')
def index():
    inicializar_jogo()

    # Renderiza o HTML usando a string definida no topo do arquivo
    return render_template_string(
        HTML_TEMPLATE,
        red_cartas=RED_TEAM_CARTAS,
        blue_cartas=BLUE_TEAM_CARTAS,
        placar_red=session.get('placar_red'),
        placar_blue=session.get('placar_blue'),
        rodada=session.get('rodada'),
        historico=session.get('historico', [])
    )


@app.route('/jogar', methods=['POST'])
def jogar():
    inicializar_jogo()

    ataque = request.form.get('ataque')
    defesa = request.form.get('defesa')

    if not ataque or not defesa:
        session['mensagem'] = "Selecione uma carta de Ataque e uma de Defesa para jogar."
        return redirect(url_for('index'))

    # Calcula a pontuação e resultado
    pontos_red, pontos_blue, resultado_texto = calcular_pontuacao(ataque, defesa)

    # Atualiza o placar e histórico
    session['placar_red'] += pontos_red
    session['placar_blue'] += pontos_blue

    rodada_info = {
        'rodada': session['rodada'],
        'ataque': RED_TEAM_CARTAS[ataque],
        'defesa': BLUE_TEAM_CARTAS[defesa],
        'resultado': resultado_texto,
        'pontos_red': pontos_red,
        'pontos_blue': pontos_blue
    }
    session['historico'].append(rodada_info)

    session['mensagem'] = f"Rodada {session['rodada']}: {resultado_texto} (Red +{pontos_red}, Blue +{pontos_blue})"

    session['rodada'] += 1
    session.modified = True

    return redirect(url_for('index'))


@app.route('/reset')
def reset():
    """Limpa a sessão e reinicia o jogo."""
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    print("Iniciando Ciberbatalha...")
    # Execute 'python app.py' no terminal
    app.run(debug=True)
