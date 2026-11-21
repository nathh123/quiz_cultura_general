import json
import os
import random
import time
import tkinter as tk
from tkinter import messagebox

ARCHIVO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preguntas.json")
NUM_PREGUNTAS = 5
VIDAS_INICIALES = 3
PUNTOS_POR_ACIERTO = 10
FUENTE_PREGUNTA = ("Times New Roman", 20)
COLOR_TEXTO = "black"
def cargar_preguntas():
    "Lee TODAS las preguntas del archivo. Devuelve lista o None si hay error."
    try:
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            datos = json.load(f)
    except FileNotFoundError:
        messagebox.showerror("Error", f"No se encontró el archivo de datos:\n{ARCHIVO}")
        return None
    except json.JSONDecodeError:
        messagebox.showerror("Error", "El archivo preguntas.json tiene un formato inválido.")
        return None
    if not isinstance(datos, list):
        messagebox.showerror("Error", "El archivo preguntas.json debe contener una lista.")
        return None
    return datos
class QuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quiz de Cultura General")
        self.geometry("560x380")
        self.resizable(False, False)
        self.preguntas = []
        self.indice = 0
        self.puntaje = 0
        self.vidas = VIDAS_INICIALES
        self.inicio_tiempo = 0.0
        self.opciones_actuales = []
        self.seleccion = tk.IntVar(value=-1)
        self.vista_inicio = tk.Frame(self)
        self.vista_juego = tk.Frame(self)
        self.vista_resultados = tk.Frame(self)
        self._construir_inicio()
        self._construir_juego()
        self._construir_resultados()
        self.mostrar(self.vista_inicio)
    #Vistas
    def mostrar(self, vista):
        for v in (self.vista_inicio, self.vista_juego, self.vista_resultados):
            v.pack_forget()
        vista.pack(fill="both", expand=True, padx=20, pady=20)
    def _construir_inicio(self):
        tk.Label(self.vista_inicio, text="Quiz de Cultura General",
                 font=("Times New Roman", 24, "bold"), fg=COLOR_TEXTO).pack(pady=(70, 20))
        tk.Button(self.vista_inicio, text="Comenzar", font=("Arial", 14),
                  command=self.comenzar).pack()
    def _construir_juego(self):
        f = self.vista_juego
        f.columnconfigure(0, weight=1)
        f.columnconfigure(1, weight=1)
        self.lbl_contador = tk.Label(f, text="", font=("Arial", 11))
        self.lbl_contador.grid(row=0, column=0, sticky="w")
        self.lbl_estado = tk.Label(f, text="", font=("Arial", 11))
        self.lbl_estado.grid(row=0, column=1, sticky="e")
        self.lbl_pregunta = tk.Label(f, text="", font=FUENTE_PREGUNTA, fg=COLOR_TEXTO,
                                     wraplength=500, justify="left")
        self.lbl_pregunta.grid(row=1, column=0, columnspan=2, sticky="w", pady=15)
        self.radios = []
        for i in range(4):
            rb = tk.Radiobutton(f, text="", variable=self.seleccion, value=i,
                                font=("Arial", 12), anchor="w")
            rb.grid(row=2 + i, column=0, columnspan=2, sticky="w", pady=2)
            self.radios.append(rb)
        tk.Button(f, text="Responder", font=("Arial", 12),
                  command=self.responder).grid(row=6, column=0, columnspan=2, pady=15)
    def _construir_resultados(self):
        f = self.vista_resultados
        tk.Label(f, text="Resultados", font=("Times New Roman", 22, "bold"),
                 fg=COLOR_TEXTO).pack(pady=(30, 10))
        self.lbl_resumen = tk.Label(f, text="", font=("Arial", 13), justify="center")
        self.lbl_resumen.pack(pady=10)
        tk.Button(f, text="Jugar de nuevo", font=("Arial", 12),
                  command=lambda: self.mostrar(self.vista_inicio)).pack(pady=5)
        tk.Button(f, text="Salir", font=("Arial", 12), command=self.destroy).pack(pady=5)
    #logica
    def comenzar(self):
        todas = cargar_preguntas()
        if todas is None:
            return  # aqui se muestra error asi no se inicia el juego
        if len(todas) < NUM_PREGUNTAS:
            messagebox.showerror(
                "Error",
                f"El archivo tiene {len(todas)} preguntas y se necesitan al menos {NUM_PREGUNTAS}.")
            return
        self.preguntas = random.sample(todas, NUM_PREGUNTAS)
        self.indice = 0
        self.puntaje = 0
        self.vidas = VIDAS_INICIALES
        self.inicio_tiempo = time.time()
        self.mostrar(self.vista_juego)
        self.mostrar_pregunta()
    def mostrar_pregunta(self):
        p = self.preguntas[self.indice]
        # Se barajan las opciones guardando cuál es la correcta
        self.opciones_actuales = list(enumerate(p["opciones"]))
        random.shuffle(self.opciones_actuales)
        self.lbl_contador.config(text=f"Pregunta {self.indice + 1} de {len(self.preguntas)}")
        self.lbl_estado.config(text=f"Puntaje: {self.puntaje}   Vidas: {self.vidas}")
        self.lbl_pregunta.config(text=p["pregunta"])
        self.seleccion.set(-1)
        for rb, (_, texto) in zip(self.radios, self.opciones_actuales):
            rb.config(text=texto)
    def responder(self):
        elegido = self.seleccion.get()
        if elegido == -1:
            messagebox.showwarning("Aviso", "Selecciona una opción.")
            return
        indice_original = self.opciones_actuales[elegido][0]
        if indice_original == self.preguntas[self.indice]["correcta"]:
            self.puntaje += PUNTOS_POR_ACIERTO
        else:
            self.vidas -= 1
        self.indice += 1
        if self.vidas == 0 or self.indice >= len(self.preguntas):
            self.terminar()
        else:
            self.mostrar_pregunta()
    def terminar(self):
        total = time.time() - self.inicio_tiempo
        motivo = "Te quedaste sin vidas." if self.vidas == 0 else "¡Terminaste todas las preguntas!"
        texto = (f"{motivo}\n\nPuntaje: {self.puntaje}\nVidas restantes: {self.vidas}\n"
                 f"Tiempo total: {total:.1f} segundos")
        self.lbl_resumen.config(text=texto)
        self.mostrar(self.vista_resultados)
        messagebox.showinfo("Fin del juego", texto)
if __name__ == "__main__":
    QuizApp().mainloop()
