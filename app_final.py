import os
import shutil
import pandas as pd
import re
from datetime import datetime, time, timedelta
import holidays
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import subprocess
import json
from PIL import Image, ImageTk  # Para usar PNG com transparência
import sys


def resource_path(relative_path):
    """Ajusta caminho para funcionar no .exe do PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# =============================
# CONFIGURAÇÕES
# =============================
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

ARQ_FUNCIONARIOS = "dados_funcionarios.json"

funcionario_especial = {
    "12345678911": "JOAQUIM DO NASCIMENTO",
    "11122233344": "MARIA APARECIDA DOS SANTOS",
}
cpfs_alvo = list(funcionario_especial.keys())
funcionarios_ate_1315 = ["12345678911", "11122233344"]
# CPFs que terão hora extra por entrada antes das 07:00
cpfs_extra_inicio = ["11122233344"]

limite_normal = time(13, 15)
limite_demais = time(17, 0)

# Variável global de funcionários
funcionarios = {}

def carregar_funcionarios():
    """Carrega o JSON atualizado de funcionários para a variável global"""
    global funcionarios
    if os.path.exists(ARQ_FUNCIONARIOS):
        with open(ARQ_FUNCIONARIOS, "r", encoding="utf-8") as f:
            try:
                funcionarios = json.load(f)
            except json.JSONDecodeError:
                funcionarios = {}
                messagebox.showerror(
                    "Erro",
                    "⚠ O arquivo de funcionários está corrompido!\n\n"
                    "Corrija manualmente o arquivo 'dados_funcionarios.json'."
                )
    else:
        funcionarios = {}
        with open(ARQ_FUNCIONARIOS, "w", encoding="utf-8") as f:
            json.dump(funcionarios, f, ensure_ascii=False, indent=4)


def cadastrar_funcionario():
    carregar_funcionarios()

    top = tk.Toplevel()
    top.title("Cadastro de Funcionário")
    top.geometry("300x300")          # tamanho fixo
    top.resizable(False, False)      # trava redimensionamento
    top.grab_set()                   # deixa modal

    cpf_var = tk.StringVar()
    nome_var = tk.StringVar()
    matricula_var = tk.StringVar()
    funcao_var = tk.StringVar()
    setor_var = tk.StringVar()

    def processar():
        cpf = cpf_var.get()
        nome = nome_var.get()
        matricula = matricula_var.get()
        funcao = funcao_var.get()
        setor = setor_var.get()

        # Validações
        if not cpf or not cpf.isdigit() or len(cpf) != 11:
            messagebox.showwarning("Erro", "CPF deve conter exatamente 11 números!", parent=top)
            return
        if cpf in funcionarios:
            messagebox.showwarning("Aviso", "CPF já cadastrado!", parent=top)
            return
        if not nome or not nome.replace(" ", "").isalpha():
            messagebox.showwarning("Erro", "Nome deve conter apenas letras e espaços!", parent=top)
            return
        if not matricula or not matricula.isdigit():
            messagebox.showwarning("Erro", "Matrícula deve conter apenas números!", parent=top)
            return
        if not funcao or not setor:
            messagebox.showwarning("Erro", "Função e Setor não podem estar vazios!", parent=top)
            return

        funcionarios[cpf] = {
            "nome": nome.upper(),
            "matricula": matricula,
            "funcao": funcao.upper(),
            "setor": setor.upper()
        }
        with open(ARQ_FUNCIONARIOS, "w", encoding="utf-8") as f:
            json.dump(funcionarios, f, ensure_ascii=False, indent=4)

        messagebox.showinfo("Sucesso", f"Funcionário {nome.upper()} cadastrado!", parent=top)
        top.destroy()

    # Layout da janela
    tk.Label(top, text="CPF:").pack(pady=2)
    tk.Entry(top, textvariable=cpf_var).pack(pady=2)
    tk.Label(top, text="Nome:").pack(pady=2)
    tk.Entry(top, textvariable=nome_var).pack(pady=2)
    tk.Label(top, text="Matrícula:").pack(pady=2)
    tk.Entry(top, textvariable=matricula_var).pack(pady=2)
    tk.Label(top, text="Função:").pack(pady=2)
    tk.Entry(top, textvariable=funcao_var).pack(pady=2)
    tk.Label(top, text="Setor:").pack(pady=2)
    tk.Entry(top, textvariable=setor_var).pack(pady=2)

    tk.Button(top, text="Cadastrar", command=processar, bg="#4CAF50", fg="white").pack(pady=10)


def excluir_funcionario():
    carregar_funcionarios()

    top = tk.Toplevel()
    top.title("Excluir Funcionário")
    top.geometry("300x150")         # tamanho fixo
    top.resizable(False, False)     # trava redimensionamento
    top.grab_set()                  # modal

    cpf_var = tk.StringVar()

    def processar():
        cpf = cpf_var.get()
        if not cpf:
            return
        if cpf not in funcionarios:
            messagebox.showwarning("Aviso", "CPF não encontrado!", parent=top)
            return

        nome = funcionarios[cpf]["nome"]
        del funcionarios[cpf]

        with open(ARQ_FUNCIONARIOS, "w", encoding="utf-8") as f:
            json.dump(funcionarios, f, ensure_ascii=False, indent=4)

        messagebox.showinfo("Sucesso", f"Funcionário {nome} removido!", parent=top)
        top.destroy()

    tk.Label(top, text="Digite o CPF a remover:").pack(pady=10)
    tk.Entry(top, textvariable=cpf_var).pack(pady=5)
    tk.Button(top, text="Excluir", command=processar, bg="#f44336", fg="white").pack(pady=10)

def selecionar_arquivo():
    global arquivo_processado
    caminho = filedialog.askopenfilename(filetypes=[("TXT Files", "*.txt")])
    if caminho:
        nome_arquivo = os.path.basename(caminho)
        destino = os.path.join(UPLOAD_DIR, nome_arquivo)
        shutil.copy(caminho, destino)
        arquivo_processado = destino
        processar(destino)


def calcular_horas_ou_extra(row):
    day = row['data'].date() if hasattr(row['data'], 'date') else row['data']
    t1_time = datetime.strptime(row['hora_entrada'], "%H:%M:%S").time()
    t2_time = datetime.strptime(row['hora_saida'], "%H:%M:%S").time()
    t1 = datetime.combine(day, t1_time)
    t2 = datetime.combine(day, t2_time)

    limite_inicio = datetime.combine(day, time(7, 0))
    limite_1315 = datetime.combine(day, limite_normal)
    limite_1700 = datetime.combine(day, limite_demais)

    if row['data'].weekday() < 5 and row['data'] not in feriados_lista:
        extra = timedelta()

        # Extra antes das 07:00 somente para CPFs em cpfs_extra_inicio
        if row['cpf'] in cpfs_extra_inicio and t1 < limite_inicio:
            extra += (limite_inicio - t1)

        # Extra após limite do dia útil (13:15 para especiais, 17:00 para os demais)
        if row['cpf'] in funcionarios_ate_1315:
            if t2 > limite_1315:
                extra += (t2 - limite_1315)
        else:
            if t2 > limite_1700:
                extra += (t2 - limite_1700)

        return str(extra)[:-3] if extra > timedelta() else "00:00"
    else:
        # Sábado, domingo e feriado = todas as horas contam
        return str(t2 - t1)[:-3]


def processar(arquivo):
    global df_relatorio, feriados_lista
    try:
        carregar_funcionarios()

        # 🔧 Tentativa automática de leitura conforme a codificação do arquivo
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                linhas = f.readlines()
            print("✅ Arquivo lido com codificação UTF-8")
        except UnicodeDecodeError:
            with open(arquivo, "r", encoding="latin1") as f:
                linhas = f.readlines()
            print("⚠️ Arquivo lido com codificação LATIN-1 (Windows-1252)")

        dados = []
        padrao = re.compile(r"^(\d{10})\s*(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})-0300(\d{11})")
        for linha in linhas:
            match = padrao.search(linha)
            if match:
                id_registro, data, hora, cpf = match.groups()
                if cpf in funcionarios:
                    dados.append([id_registro, data, hora, cpf])

        df = pd.DataFrame(dados, columns=["id", "data", "hora", "cpf"])
        df = df.sort_values(by=["cpf", "data", "hora"])

        df["hora_shift"] = df.groupby(["cpf", "data"])["hora"].shift()
        df = df[df["hora"] != df["hora_shift"]].drop(columns="hora_shift")

        primeira = df.groupby(["cpf", "data"]).first().reset_index()
        ultima = df.groupby(["cpf", "data"]).last().reset_index()

        df_final = primeira.rename(columns={"hora": "hora_entrada"})
        df_final["hora_saida"] = ultima["hora"]
        df_final["data"] = pd.to_datetime(df_final["data"])

        anos_presentes = df_final["data"].dt.year.unique().tolist()
        feriados = holidays.Brazil(years=anos_presentes, prov="SP")
        feriados_lista = pd.to_datetime(list(feriados.keys()))

        df_final["horas_trabalhadas"] = df_final.apply(calcular_horas_ou_extra, axis=1)

        df_relatorio = df_final[
            (df_final["data"].dt.dayofweek >= 5) | (df_final["data"].isin(feriados_lista))
        ].copy()

        df_uteis = df_final[
            (df_final["cpf"].isin(funcionarios_ate_1315)) &
            (df_final["data"].dt.dayofweek < 5) &
            (~df_final["data"].isin(feriados_lista))
        ].copy()

        df_uteis_demais = df_final[
            (df_final["cpf"].isin([cpf for cpf in funcionarios if cpf not in funcionarios_ate_1315])) &
            (df_final["data"].dt.dayofweek < 5) &
            (~df_final["data"].isin(feriados_lista))
        ].copy()

        df_relatorio = pd.concat([df_relatorio, df_uteis, df_uteis_demais]).sort_values(by=["cpf", "data"])

        btn_relatorio.config(state="normal")
        btn_resumo_txt.config(state="normal")
        btn_resumo_json.config(state="normal")

        messagebox.showinfo("Sucesso", "Arquivo processado! Agora escolha onde salvar os relatórios.")

    except Exception as e:
        messagebox.showerror("Erro", f"⚠ Ocorreu um erro ao processar o arquivo:\n\n{e}")


def salvar_relatorio_final():
    if df_relatorio is None:
        messagebox.showerror("Erro", "Nenhum arquivo processado ainda.")
        return
    destino = filedialog.asksaveasfilename(
        title="Salvar Relatório Final",
        initialfile="relatorio_final.txt",
        defaultextension=".txt",
        filetypes=[("Arquivos de texto", "*.txt")]
    )
    if destino:
        with open(destino, "w", encoding="utf-8") as f:
            for _, row in df_relatorio.iterrows():
                f.write(f"{funcionarios[row['cpf']]['nome']} {row['data'].date()} {row['hora_entrada']} {row['hora_saida']} {row['horas_trabalhadas']}\n")
        messagebox.showinfo("Sucesso", f"Relatório Final salvo em:\n{destino}")


def salvar_resumo_geral_txt():
    if df_relatorio is None:
        messagebox.showerror("Erro", "Nenhum arquivo processado ainda.")
        return

    def formatar_tempo_str(td):
        if isinstance(td, str):
            partes = td.split(":")
            h, m = (map(int, partes[:2]))
            td = timedelta(hours=h, minutes=m)
        total_minutos = int(td.total_seconds() // 60)
        horas, minutos = divmod(total_minutos, 60)
        return f"{horas:02d}:{minutos:02d}"

    destino = filedialog.asksaveasfilename(
        title="Salvar Resumo Geral (TXT)",
        initialfile="resumo_geral.txt",
        defaultextension=".txt",
        filetypes=[("Arquivos de texto", "*.txt")]
    )
    if destino:
        with open(destino, "w", encoding="utf-8") as f_out:
            f_out.write("RELATÓRIO RESUMIDO\n\n")
            for cpf, dados in funcionarios.items():
                df_func = df_relatorio[df_relatorio["cpf"] == cpf]
                if not df_func.empty:
                    total_50 = timedelta()
                    total_100 = timedelta()
                    for _, row in df_func.iterrows():
                        delta = formatar_tempo_str(row["horas_trabalhadas"])
                        h, m = map(int, delta.split(":"))
                        delta = timedelta(hours=h, minutes=m)
                        if row["data"].weekday() == 5:
                            total_50 += delta
                        elif row["data"].weekday() == 6:
                            total_100 += delta
                        else:
                            total_50 += delta
                    total_geral = total_50 + total_100
                    f_out.write(f"{dados['nome']}\n")
                    f_out.write(f"Horas 50% {formatar_tempo_str(total_50)}\n")
                    f_out.write(f"Horas 100% {formatar_tempo_str(total_100)}\n")
                    f_out.write(f"Total de horas {formatar_tempo_str(total_geral)}\n\n")
        messagebox.showinfo("Sucesso", f"Resumo Geral em TXT salvo em:\n{destino}")


def salvar_resumo_geral_json():
    if df_relatorio is None:
        messagebox.showerror("Erro", "Nenhum arquivo processado ainda.")
        return

    def formatar_tempo_str(td):
        if isinstance(td, str):
            partes = td.split(":")
            h, m = (map(int, partes[:2]))
            td = timedelta(hours=h, minutes=m)
        total_minutos = int(td.total_seconds() // 60)
        horas, minutos = divmod(total_minutos, 60)
        return f"{horas:02d}:{minutos:02d}"

    resumo = []
    for cpf, dados in funcionarios.items():
        df_func = df_relatorio[df_relatorio["cpf"] == cpf]
        if not df_func.empty:
            total_50 = timedelta()
            total_100 = timedelta()
            for _, row in df_func.iterrows():
                delta = formatar_tempo_str(row["horas_trabalhadas"])
                h, m = map(int, delta.split(":"))
                delta = timedelta(hours=h, minutes=m)
                if row["data"].weekday() == 5:
                    total_50 += delta
                elif row["data"].weekday() == 6:
                    total_100 += delta
                else:
                    total_50 += delta
            if total_50 > timedelta() or total_100 > timedelta():
                resumo.append({
                    "cpf": cpf,
                    "nome": dados["nome"],
                    "matricula": dados["matricula"],
                    "funcao": dados["funcao"],
                    "setor": dados["setor"],
                    "horas_50": formatar_tempo_str(total_50),
                    "horas_100": formatar_tempo_str(total_100),
                    "total": formatar_tempo_str(total_50 + total_100)
                })

    destino = filedialog.asksaveasfilename(
        title="Salvar Resumo Geral (JSON)",
        initialfile="resumo_geral.json",
        defaultextension=".json",
        filetypes=[("Arquivos JSON", "*.json")]
    )

    if destino:
        with open(destino, "w", encoding="utf-8") as f:
            json.dump(resumo, f, ensure_ascii=False, indent=4)
        messagebox.showinfo("Sucesso", f"Resumo Geral em JSON salvo em:\n{destino}")


def abrir_pasta_uploads():
    subprocess.Popen(f'explorer "{os.path.abspath(UPLOAD_DIR)}"')

def sair():
    root.destroy()  # fecha a janela e encerra o programa


# =============================
# INTERFACE TKINTER
# =============================
root = tk.Tk()
root.title("Processador de Horas Extras")
root.geometry("420x530")
root.config(background = "#f0f0f0")
root.resizable(False, False)

btn_upload = tk.Button(root, text="SELECIONAR\nARQUIVO\n(TXT)", width=14, height=3, bg = "#dddddd", fg = "#333333", border = 4, font=("Bahnschrift Light", 12, "bold"), command=selecionar_arquivo)
btn_upload.pack(pady=8)
btn_upload.place(x=30, y=20)

btn_relatorio = tk.Button(root, text="SALVAR\nRELATÓRIO\nDETALHADO", width=14, height=3, bg = "#dddddd", fg = "#333333", border = 4, font=("Bahnschrift Light", 12, "bold"), state="disabled", command=salvar_relatorio_final)
btn_relatorio.pack(pady=8)
btn_relatorio.place(x=240, y=20)

btn_resumo_txt = tk.Button(root, text="SALVAR RESUMO\nGERAL (TXT)", width=14, height=3, bg = "#dddddd", fg = "#333333", border = 4, font=("Bahnschrift Light", 12, "bold"), state="disabled", command=salvar_resumo_geral_txt)
btn_resumo_txt.pack(pady=10)
btn_resumo_txt.place(x=30, y=110)

btn_resumo_json = tk.Button(root, text="SALVAR RESUMO\nGERAL (JSON)", width=14, height=3, bg = "#dddddd", fg = "#333333", border = 4, font=("Bahnschrift Light", 12, "bold"), state="disabled", command=salvar_resumo_geral_json)
btn_resumo_json.pack(pady=10)
btn_resumo_json.place(x=240, y=110)

# Botão cadastrar funcionário
btn_cadastrar = tk.Button(root, text="CADASTRAR\nFUNCIONÁRIO", width=15, height=2, bg="#baf13e", fg="#333333", border = 4,  font=("Bahnschrift Light", 11, "bold"), command=cadastrar_funcionario)
btn_cadastrar.pack(pady=10)
btn_cadastrar.place(x=30, y=290)

# Botão excluir funcionário
btn_excluir = tk.Button(root, text="EXCLUIR\nFUNCIONÁRIO", width=15, height=2, bg="#ff7171", fg="#333333", border = 4,  font=("Bahnschrift Light", 11, "bold"), command=excluir_funcionario)
btn_excluir.pack(pady=10)
btn_excluir.place(x=30, y=360)

btn_pasta = tk.Button(root, text="ABRIR PASTA\nUPLOADS", width=14, height=3, bg = "#035b96", fg = "white", border = 4, font=("Bahnschrift Light", 12, "bold"), command=abrir_pasta_uploads)
btn_pasta.pack(pady=10)
btn_pasta.place(x=30, y=200)

btn_sair = tk.Button(root, text="Sair", width=14, height=1, bg = "#035b96", fg = "white", border = 4, font=("Bahnschrift Light", 12, "bold"), command=sair)
btn_sair.pack(pady=8)
btn_sair.place(x=240, y=460)

# Criar a Label
label = tk.Label(root, text="Todos os direitos reservados Luiz Cruz 2025  V 1.0.0", font=("Microsoft Himalaya", 14, "bold"), fg="grey")
label.pack()
label.place(x=100, y=510) 

root.mainloop()
