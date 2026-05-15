from flask import Flask, request, send_from_directory, jsonify
import os

# Localiza a pasta 'src' onde este ficheiro está
current_dir = os.path.dirname(os.path.abspath(__file__))

# Localiza a raiz do projeto (um nível acima de 'src')
project_root = os.path.dirname(current_dir)

app = Flask(
    __name__, 
    static_folder=os.path.join(current_dir, "public"), 
    static_url_path=""
)

# Define o caminho das submissões para fora da 'src'
BASE_SUBMISSIONS = os.path.join(project_root, "submissoes")

folders = ["p1", "p2", "p3"]
for f in folders:
    os.makedirs(os.path.join(BASE_SUBMISSIONS, f), exist_ok=True)

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "arquivo" not in request.files:
        return jsonify({"erro": "Nenhum ficheiro enviado"}), 400
    
    file = request.files["arquivo"]
    aluno = request.form.get("aluno", "anonimo").strip().replace(" ", "_")
    problema = request.form.get("problema")

    if problema not in folders:
        return jsonify({"erro": "Problema inválido"}), 400
    
    if file.filename == "":
        return jsonify({"erro": "Nome do ficheiro vazio"}), 400

    if file:
        filename = f"{aluno}_{file.filename}"
        # Salva na pasta raiz/submissoes/pX/
        save_path = os.path.join(BASE_SUBMISSIONS, problema, filename)
        file.save(save_path)
        return jsonify({
            "mensagem": f"Código para {problema} enviado com sucesso!", 
            "arquivo": filename
        }), 200

if __name__ == "__main__":
    # Porta 8080 para evitar conflitos de permissão no Windows
    app.run(host="0.0.0.0", port=8080, debug=True)