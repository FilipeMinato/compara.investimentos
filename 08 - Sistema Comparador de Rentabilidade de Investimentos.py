"""
Simulador de Projeção de Investimentos com Interface Tkinter
-------------------------------------------------------------
Este aplicativo permite simular o crescimento de um investimento com:
- Aporte mensal
- Aporte inicial
- Aportes extras (opcionais: anual ou semestral)
- Baseado em rendimentos médios dos últimos 2 anos (Yahoo Finance)

Ele exibe o valor final projetado para diferentes investimentos.
Não se trata de recomendação financeira, apenas uma ferramenta comparativa.
"""

import tkinter as tk
from tkinter import messagebox, ttk
import yfinance as yf
from datetime import datetime, timedelta

# Calcula o rendimento médio anual de um ativo dos últimos 2 anos
def rendimento_anual_medio(ticker):
    hoje = datetime.today()
    dois_anos_atras = hoje - timedelta(days=730)
    dados = yf.download(ticker, start=dois_anos_atras.strftime('%Y-%m-%d'), end=hoje.strftime('%Y-%m-%d'))

    if dados.empty or 'Close' not in dados.columns:
        return None

    preco_inicio = float(dados['Close'].iloc[0])
    preco_fim = float(dados['Close'].iloc[-1])
    rendimento_total = (preco_fim / preco_inicio) - 1
    rendimento_anual = (1 + rendimento_total) ** (1 / 2) - 1  # Transformando para taxa anual equivalente
    return float(rendimento_anual * 100)

# Faz a simulação do valor acumulado ao longo dos meses
def calcula_valor_final(aplicacao_mensal, meses, taxa_aa, aporte_inicial, aporte_extra, tipo_aporte):
    taxa_mensal = (1 + taxa_aa / 100) ** (1 / 12) - 1
    total = aporte_inicial
    for mes in range(1, meses + 1):
        total = total * (1 + taxa_mensal) + aplicacao_mensal
        if tipo_aporte == 1 and mes % 12 == 0:
            total += aporte_extra
        elif tipo_aporte == 2 and mes % 6 == 0:
            total += aporte_extra
    return total

# Abre uma nova janela para preencher os dados da simulação
def abrir_popup_simulacao():
    popup = tk.Toplevel(root)
    popup.title("Nova Simulação")
    popup.geometry("350x350")
    popup.grab_set()  # Impede interação com a janela principal enquanto o popup está aberto

    # Campos de entrada
    tk.Label(popup, text="Aplicação mensal (R$):").pack()
    ent_mensal = tk.Entry(popup)
    ent_mensal.pack()

    tk.Label(popup, text="Prazo (meses):").pack()
    ent_prazo = tk.Entry(popup)
    ent_prazo.pack()

    tk.Label(popup, text="Aporte inicial (R$):").pack()
    ent_inicial = tk.Entry(popup)
    ent_inicial.pack()

    # Tipo de aporte extra (opcional)
    tk.Label(popup, text="Tipo de aporte extra:").pack()
    combo_tipo = ttk.Combobox(popup, values=["0 - Nenhum", "1 - Anual", "2 - Semestral"], state="readonly")
    combo_tipo.pack()
    combo_tipo.current(0)

    lbl_extra = tk.Label(popup, text="Valor do aporte extra (R$):")
    ent_extra = tk.Entry(popup)

    # Mostra ou esconde o campo do aporte extra dependendo da seleção
    def atualizar_visibilidade_aporte_extra(event=None):
        tipo = combo_tipo.get().split(" - ")[0]
        if tipo == "0":
            lbl_extra.pack_forget()
            ent_extra.pack_forget()
        else:
            lbl_extra.pack()
            ent_extra.pack()

    combo_tipo.bind("<<ComboboxSelected>>", atualizar_visibilidade_aporte_extra)
    atualizar_visibilidade_aporte_extra()

    # Executa a simulação após preencher os dados
    def executar_simulacao():
        try:
            valor_mensal = float(ent_mensal.get().replace(',', '.'))
            prazo = int(ent_prazo.get())
            aporte_inicial = float(ent_inicial.get().replace(',', '.'))
            tipo_aporte = int(combo_tipo.get().split(" - ")[0])

            if tipo_aporte == 0:
                aporte_extra = 0
            else:
                aporte_extra = float(ent_extra.get().replace(',', '.'))

            # Validação básica
            if valor_mensal < 0 or prazo <= 0 or aporte_inicial < 0 or aporte_extra < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Preencha os valores corretamente.")
            return

        # Limpa resultados anteriores
        texto_resultado.delete(*texto_resultado.get_children())

        # Faz o cálculo para cada ativo e exibe
        for investimento, taxa in rendimentos_aa.items():
            valor_final = calcula_valor_final(valor_mensal, prazo, taxa, aporte_inicial, aporte_extra, tipo_aporte)
            texto_resultado.insert("", "end", values=(investimento, f"{taxa:.2f}%", f"R$ {valor_final:,.2f}"))

        aviso_label.config(
            text="Simulação baseada nos rendimentos médios dos últimos 24 meses.\nNão se trata de recomendação de investimento."
        )
        popup.destroy()

    # Botão para iniciar simulação
    tk.Button(popup, text="Simular", command=executar_simulacao, bg="green", fg="white").pack(pady=10)

# Interface principal da aplicação
root = tk.Tk()
root.title("Comparador de Projeção de Investimentos")
root.geometry("700x450")
root.resizable(False, False)

# Botão para abrir nova simulação
btn_nova = tk.Button(root, text="Nova Simulação", command=abrir_popup_simulacao, bg="blue", fg="white", font=("Arial", 12))
btn_nova.pack(pady=10)

# Tabela de resultados
texto_resultado = ttk.Treeview(root, columns=("Investimento", "Rendimento", "Valor Final"), show='headings')
texto_resultado.heading("Investimento", text="Investimento")
texto_resultado.heading("Rendimento", text="Rendimento Anual")
texto_resultado.heading("Valor Final", text="Valor Final")

texto_resultado.column("Investimento", width=220)
texto_resultado.column("Rendimento", width=160)
texto_resultado.column("Valor Final", width=220)

texto_resultado.pack(pady=10)

# Aviso legal no rodapé
aviso_label = tk.Label(root, text="", fg="gray", font=("Arial", 10), justify="center")
aviso_label.pack(pady=5)

# Carrega os rendimentos médios ao iniciar o programa
def carregar_dados():
    loading = tk.Toplevel(root)
    loading.title("Carregando")
    tk.Label(loading, text="Obtendo rendimentos dos últimos 2 anos...\nIsso pode levar alguns segundos...").pack(padx=20, pady=20)
    loading.update()

    global rendimentos_aa
    rendimentos_aa = {
        'Renda Fixa (simulada)': 7.0,  # valor fixo fictício
        'Poupança (simulada)': 5.0,    # valor fixo fictício
        'Ações PETR4': rendimento_anual_medio('PETR4.SA'),
        'FII HGLG11': rendimento_anual_medio('HGLG11.SA')
    }

    # Remove ativos com erro de conexão ou dados
    rendimentos_aa = {k: v for k, v in rendimentos_aa.items() if v is not None}
    loading.destroy()

# Carregamento inicial dos dados de rendimento
carregar_dados()

# Inicia o loop da interface
root.mainloop()
