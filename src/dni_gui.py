"""
Aplicación gráfica para DNI español con tkinter.

Permite:
- Calcular la letra de un DNI introduciendo el número.
- Validar un DNI completo (número + letra).
- Generar un DNI aleatorio válido.
- Generar lotes con exportación y formato configurable.

Diseño moderno con paleta de colores y feedback visual.
Incluye aviso legal sobre uso de DNIs ficticios.
"""

import logging
import sys
import threading
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import tkinter as tk

from src.config import (
    ALTURA_LOGO_TITULO_PX,
    COLORES,
    LOTE_MAX,
    LOTE_MIN,
    SEPARADORES,
    WINDOW_MIN_HEIGHT,
    WINDOW_MIN_WIDTH,
    WINDOW_TITLE,
)
from src.dni import (
    calcular_letra_dni,
    generar_dni_aleatorio,
    generar_dni_lote,
    truncar_para_clipboard,
    validar_dni_completo,
)

logger = logging.getLogger(__name__)


def _ruta_base_recursos() -> Path:
    """
    Devuelve la carpeta donde están los recursos empaquetados.

    En ejecución normal es la raíz del repositorio; con PyInstaller (--onefile)
    es la carpeta temporal ``sys._MEIPASS``.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parent.parent


def _aplicar_icono_ventana(root: tk.Tk) -> None:
    """
    Asigna el icono de la ventana (barra de título y, en Windows, barra de tareas).

    Usa ``assets/icon.ico`` en Windows; en otros sistemas intenta ``icon.png``
    con ``iconphoto`` si existe.
    """
    base = _ruta_base_recursos() / "assets"
    ico = base / "icon.ico"
    png = base / "icon.png"
    try:
        if sys.platform == "win32" and ico.is_file():
            root.iconbitmap(default=str(ico))
            return
        if png.is_file():
            foto = tk.PhotoImage(file=str(png))
            root.iconphoto(True, foto)
            root._icono_app_ref = foto  # type: ignore[attr-defined]
    except tk.TclError as exc:
        logger.debug("Icono de ventana no disponible: %s", exc)


def _logo_titulo_photoimage() -> tk.PhotoImage | None:
    """
    Carga ``assets/icon.png`` y lo reduce para colocarlo junto al título.

    Usa ``subsample`` de tkinter (sin Pillow). Si el PNG no se puede cargar,
    devuelve None.
    """
    png = _ruta_base_recursos() / "assets" / "icon.png"
    if not png.is_file():
        return None
    try:
        foto = tk.PhotoImage(file=str(png))
    except tk.TclError as exc:
        logger.debug("Logo de título: PNG no cargado: %s", exc)
        return None
    ancho, alto = foto.width(), foto.height()
    if ancho <= 0 or alto <= 0:
        return foto
    lado_max = max(ancho, alto)
    factor = max(1, lado_max // ALTURA_LOGO_TITULO_PX)
    if factor <= 1:
        return foto
    return foto.subsample(factor, factor)


class DniApp:
    """
    Ventana principal de la aplicación de DNI español.

    Interfaz moderna con cálculo, validación, generación
    individual y por lotes con exportación.
    """

    def __init__(self) -> None:
        """Inicializa la ventana y los widgets."""
        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.resizable(True, True)
        self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.root.configure(bg=COLORES["fondo"])
        _aplicar_icono_ventana(self.root)

        self._generando_lote = False
        self._btn_generar_lote: ttk.Widget | None = None
        # Referencia al logo del título (evita que el GC elimine el PhotoImage)
        self._photo_logo_titulo: tk.PhotoImage | None = None

        self.root.wm_protocol("WM_DELETE_WINDOW", self._cerrar_seguro)

        self._crear_estilos()
        self._crear_widgets()

    def _cerrar_seguro(self) -> None:
        """Cierra la aplicación de forma segura."""
        self.root.quit()
        self.root.destroy()

    def _crear_estilos(self) -> None:
        """Configura estilos modernos para ttk."""
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Card.TFrame",
            background=COLORES["superficie"],
            relief="flat",
        )

        style.configure(
            "Section.TLabel",
            font=("Segoe UI", 11, "bold"),
            foreground=COLORES["texto"],
            background=COLORES["superficie"],
        )

        style.configure(
            "TLabel",
            font=("Segoe UI", 10),
            foreground=COLORES["texto"],
            background=COLORES["superficie"],
        )

        style.configure(
            "Primary.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(12, 8),
            background=COLORES["primario"],
            foreground="white",
            relief="flat",
        )
        style.map(
            "Primary.TButton",
            background=[("active", COLORES["primario_hover"])],
        )

        style.configure(
            "Secondary.TButton",
            font=("Segoe UI", 10),
            padding=(10, 6),
            background=COLORES["acento_suave"],
            foreground=COLORES["primario"],
            relief="flat",
        )

        style.configure(
            "TEntry",
            font=("Consolas", 11),
            padding=8,
            relief="flat",
        )

    def _crear_widgets(self) -> None:
        """Crea y organiza todos los widgets de la interfaz."""
        main_container = tk.Frame(
            self.root,
            bg=COLORES["fondo"],
            padx=24,
            pady=24,
        )
        main_container.pack(fill=tk.BOTH, expand=True)

        # --- Disclaimer legal ---
        disclaimer_frame = tk.Frame(main_container, bg="#fef3c7", padx=12, pady=8)
        disclaimer_frame.pack(fill=tk.X, pady=(0, 16))

        tk.Label(
            disclaimer_frame,
            text="⚠️ Aviso: Los DNIs generados son ficticios. "
            "No utilizar para fines fraudulentos ni suplantación de identidad.",
            font=("Segoe UI", 9),
            fg="#92400e",
            bg="#fef3c7",
            wraplength=500,
            justify=tk.LEFT,
        ).pack(anchor=tk.W)

        # --- Header (logo PNG + título, sin emoji) ---
        header = tk.Frame(main_container, bg=COLORES["fondo"])
        header.pack(fill=tk.X, pady=(0, 16))

        fila_titulo = tk.Frame(header, bg=COLORES["fondo"])
        fila_titulo.pack(anchor=tk.W, fill=tk.X)

        logo_img = _logo_titulo_photoimage()
        if logo_img is not None:
            self._photo_logo_titulo = logo_img  # mantener referencia viva
            tk.Label(
                fila_titulo,
                image=logo_img,
                bg=COLORES["fondo"],
            ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(
            fila_titulo,
            text=WINDOW_TITLE,
            font=("Segoe UI", 18, "bold"),
            fg=COLORES["texto"],
            bg=COLORES["fondo"],
        ).pack(side=tk.LEFT, anchor=tk.W)

        subtitulo = tk.Label(
            header,
            text="Calcula letras, valida y genera DNIs de forma segura",
            font=("Segoe UI", 10),
            fg=COLORES["texto_secundario"],
            bg=COLORES["fondo"],
        )
        subtitulo.pack(anchor=tk.W, pady=(4, 0))

        # --- Card 1: Calcular letra ---
        card1 = self._crear_card(main_container, "Calcular letra del DNI")

        input_frame = tk.Frame(card1, bg=COLORES["superficie"])
        input_frame.pack(fill=tk.X, pady=(0, 8))

        tk.Label(
            input_frame,
            text="Número (8 dígitos):",
            font=("Segoe UI", 10),
            fg=COLORES["texto"],
            bg=COLORES["superficie"],
        ).pack(side=tk.LEFT, padx=(0, 8))

        self.entry_numero = ttk.Entry(input_frame, width=14)
        self.entry_numero.pack(side=tk.LEFT, padx=(0, 8))
        self.entry_numero.bind("<Return>", lambda e: self._calcular_letra())
        self.entry_numero.bind("<KeyRelease>", self._filtrar_solo_numeros)

        ttk.Button(
            input_frame,
            text="Calcular y copiar",
            style="Primary.TButton",
            command=self._calcular_letra,
        ).pack(side=tk.LEFT)

        self.label_resultado = tk.Label(
            card1,
            text="",
            font=("Consolas", 11, "bold"),
            fg=COLORES["texto"],
            bg=COLORES["superficie"],
        )
        self.label_resultado.pack(anchor=tk.W, pady=(4, 0))

        # --- Card 2: Validar DNI completo ---
        card2 = self._crear_card(main_container, "Validar DNI completo")

        validar_frame = tk.Frame(card2, bg=COLORES["superficie"])
        validar_frame.pack(fill=tk.X, pady=(0, 8))

        tk.Label(
            validar_frame,
            text="DNI completo:",
            font=("Segoe UI", 10),
            fg=COLORES["texto"],
            bg=COLORES["superficie"],
        ).pack(side=tk.LEFT, padx=(0, 8))

        self.entry_validar = ttk.Entry(validar_frame, width=14)
        self.entry_validar.pack(side=tk.LEFT, padx=(0, 8))
        self.entry_validar.bind("<Return>", lambda e: self._validar_dni())
        self.entry_validar.bind("<KeyRelease>", self._normalizar_entrada_validar)

        ttk.Button(
            validar_frame,
            text="Validar",
            style="Secondary.TButton",
            command=self._validar_dni,
        ).pack(side=tk.LEFT)

        self.label_validacion = tk.Label(
            card2,
            text="",
            font=("Segoe UI", 10),
            bg=COLORES["superficie"],
        )
        self.label_validacion.pack(anchor=tk.W, pady=(4, 0))

        # --- Card 3: Generar aleatorio ---
        card3 = self._crear_card(main_container, "Generar DNI aleatorio")

        gen_frame = tk.Frame(card3, bg=COLORES["superficie"])
        gen_frame.pack(fill=tk.X)

        ttk.Button(
            gen_frame,
            text="Generar DNI seguro",
            style="Primary.TButton",
            command=self._generar_aleatorio,
        ).pack(side=tk.LEFT, padx=(0, 12))

        self.label_dni_generado = tk.Label(
            gen_frame,
            text="",
            font=("Consolas", 13, "bold"),
            fg=COLORES["primario"],
            bg=COLORES["superficie"],
        )
        self.label_dni_generado.pack(side=tk.LEFT)

        # --- Card 4: Generar por lotes ---
        card4 = self._crear_card(main_container, "Generar por lotes")

        lote_frame = tk.Frame(card4, bg=COLORES["superficie"])
        lote_frame.pack(fill=tk.X, pady=(0, 8))

        tk.Label(
            lote_frame,
            text="Cantidad:",
            font=("Segoe UI", 10),
            fg=COLORES["texto"],
            bg=COLORES["superficie"],
        ).pack(side=tk.LEFT, padx=(0, 8))

        self.spinbox_cantidad = tk.Spinbox(
            lote_frame,
            from_=LOTE_MIN,
            to=LOTE_MAX,
            width=8,
            font=("Consolas", 12),
            justify=tk.CENTER,
        )
        self.spinbox_cantidad.delete(0, tk.END)
        self.spinbox_cantidad.insert(0, "10")
        self.spinbox_cantidad.pack(side=tk.LEFT, padx=(0, 8))
        self.spinbox_cantidad.bind("<KeyRelease>", self._filtrar_spinbox_lote)

        self._btn_generar_lote = ttk.Button(
            lote_frame,
            text="Generar lote",
            style="Primary.TButton",
            command=self._generar_lote,
        )
        self._btn_generar_lote.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(
            lote_frame,
            text="Copiar todo",
            style="Secondary.TButton",
            command=self._copiar_lote,
        ).pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(
            lote_frame,
            text="Exportar archivo",
            style="Secondary.TButton",
            command=self._exportar_dni,
        ).pack(side=tk.LEFT)

        # Selector de separador
        sep_frame = tk.Frame(card4, bg=COLORES["superficie"])
        sep_frame.pack(fill=tk.X, pady=(4, 0))

        tk.Label(
            sep_frame,
            text="Formato exportación:",
            font=("Segoe UI", 9),
            fg=COLORES["texto_secundario"],
            bg=COLORES["superficie"],
        ).pack(side=tk.LEFT, padx=(0, 8))

        self.var_separador = tk.StringVar(value="Línea nueva")
        for sep_nombre in SEPARADORES:
            rb = tk.Radiobutton(
                sep_frame,
                text=sep_nombre,
                variable=self.var_separador,
                value=sep_nombre,
                font=("Segoe UI", 9),
                fg=COLORES["texto"],
                bg=COLORES["superficie"],
                selectcolor=COLORES["acento_suave"],
                activebackground=COLORES["superficie"],
            )
            rb.pack(side=tk.LEFT, padx=(0, 12))

        # Área de texto
        container_texto = tk.Frame(card4, bg=COLORES["superficie"])
        container_texto.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

        scrollbar = tk.Scrollbar(container_texto)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.texto_lote = tk.Text(
            container_texto,
            height=8,
            font=("Consolas", 10),
            wrap=tk.NONE,
            fg=COLORES["texto"],
            bg="#fafafa",
            relief=tk.FLAT,
            padx=8,
            pady=8,
            yscrollcommand=scrollbar.set,
        )
        self.texto_lote.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.texto_lote.yview)

        self.texto_lote.insert(tk.END, "Los DNIs generados aparecerán aquí...")
        self.texto_lote.config(fg=COLORES["texto_secundario"])

        self.label_status_lote = tk.Label(
            card4,
            text="",
            font=("Segoe UI", 9),
            fg=COLORES["texto_secundario"],
            bg=COLORES["superficie"],
        )
        self.label_status_lote.pack(anchor=tk.W, pady=(4, 0))

        # --- Footer ---
        footer = tk.Label(
            main_container,
            text="secrets.SystemRandom · Generación criptográficamente segura",
            font=("Segoe UI", 9),
            fg=COLORES["texto_secundario"],
            bg=COLORES["fondo"],
        )
        footer.pack(anchor=tk.W, pady=(16, 0))

    def _crear_card(self, parent: tk.Widget, titulo: str) -> tk.Frame:
        """Crea una tarjeta (card) con título y borde sutil."""
        card = tk.Frame(
            parent,
            bg=COLORES["superficie"],
            highlightbackground=COLORES["borde"],
            highlightthickness=1,
            padx=16,
            pady=16,
        )
        card.pack(fill=tk.X, pady=(0, 16))

        lbl = tk.Label(
            card,
            text=titulo,
            font=("Segoe UI", 11, "bold"),
            fg=COLORES["texto"],
            bg=COLORES["superficie"],
        )
        lbl.pack(anchor=tk.W, pady=(0, 12))

        return card

    def _filtrar_solo_numeros(self, _event: tk.Event) -> None:
        """Limita la entrada a máximo 8 caracteres numéricos."""
        contenido = self.entry_numero.get()
        nuevo = "".join(c for c in contenido if c.isdigit())[:8]
        if nuevo != contenido:
            self.entry_numero.delete(0, tk.END)
            self.entry_numero.insert(0, nuevo)

    def _normalizar_entrada_validar(self, _event: tk.Event) -> None:
        """Normaliza la entrada: 8 dígitos + 1 letra."""
        contenido = self.entry_validar.get().upper()
        digitos = "".join(c for c in contenido if c.isdigit())[:8]
        letras = "".join(c for c in contenido if c.isalpha())
        if len(contenido) > 8:
            letras = letras[:1]
        nuevo = (digitos + letras)[:9]
        if nuevo != contenido:
            self.entry_validar.delete(0, tk.END)
            self.entry_validar.insert(0, nuevo)

    def _filtrar_spinbox_lote(self, _event: tk.Event) -> None:
        """Limita el spinbox de cantidad a solo dígitos (máx 5)."""
        contenido = self.spinbox_cantidad.get()
        nuevo = "".join(c for c in contenido if c.isdigit())[:5]
        if nuevo != contenido:
            self.spinbox_cantidad.delete(0, tk.END)
            self.spinbox_cantidad.insert(0, nuevo)

    def _obtener_separador_actual(self) -> str:
        """Devuelve el carácter separador según la selección del usuario."""
        return SEPARADORES.get(self.var_separador.get(), "\n")

    def _copiar_al_portapapeles(self, texto: str) -> tuple[bool, bool]:
        """
        Copia texto al portapapeles de forma segura (trunca si supera el límite).

        Returns:
            Tupla (se_copió_algo, contenido_fue_truncado).
        """
        try:
            if not isinstance(texto, str) or not texto:
                return (False, False)

            texto_final, fue_truncado = truncar_para_clipboard(texto)
            if not texto_final:
                return (False, fue_truncado)

            self.root.clipboard_clear()
            self.root.clipboard_append(texto_final)
            self.root.update()

            if fue_truncado:
                logger.warning("Texto truncado al copiar (límite excedido)")
            return (True, fue_truncado)
        except Exception as e:
            logger.exception("Error al copiar al portapapeles: %s", e)
            return (False, False)

    def _calcular_letra(self) -> None:
        """Calcula y muestra la letra del DNI introducido."""
        try:
            texto = self.entry_numero.get().strip()
            if not texto:
                self._mostrar_error(
                    self.label_resultado,
                    "Introduce un número de DNI.",
                )
                return
            if len(texto) != 8:
                self._mostrar_error(
                    self.label_resultado,
                    "El DNI debe tener exactamente 8 dígitos.",
                )
                return

            letra = calcular_letra_dni(texto)
            dni_completo = f"{texto}{letra}"
            copiado, truncado = self._copiar_al_portapapeles(dni_completo)

            msg = f"Letra: {letra}  →  {dni_completo} ✓ (copiado)"
            if not copiado:
                msg = f"Letra: {letra}  →  {dni_completo} ✓"
            elif truncado:
                msg = f"Letra: {letra}  →  {dni_completo} ✓ (copiado parcial)"
            self._mostrar_exito(self.label_resultado, msg)
        except ValueError as e:
            self._mostrar_error(self.label_resultado, str(e))
        except Exception as e:
            logger.exception("Error al calcular letra: %s", e)
            self._mostrar_error(
                self.label_resultado,
                "Error inesperado. Inténtalo de nuevo.",
            )

    def _validar_dni(self) -> None:
        """Valida un DNI completo introducido por el usuario."""
        try:
            texto = self.entry_validar.get().strip().upper()
            if not texto:
                self._mostrar_error(
                    self.label_validacion,
                    "Introduce un DNI completo (8 dígitos + letra).",
                )
                return
            if len(texto) != 9:
                self._mostrar_error(
                    self.label_validacion,
                    "El DNI debe tener 9 caracteres (8 dígitos + 1 letra).",
                )
                return

            if validar_dni_completo(texto):
                self._mostrar_exito(
                    self.label_validacion,
                    f"✓ DNI válido: {texto}",
                )
            else:
                self._mostrar_error(
                    self.label_validacion,
                    "✗ DNI inválido: la letra no corresponde al número.",
                )
        except Exception as e:
            logger.exception("Error al validar DNI: %s", e)
            self._mostrar_error(
                self.label_validacion,
                "Error inesperado. Inténtalo de nuevo.",
            )

    def _generar_aleatorio(self) -> None:
        """Genera un DNI aleatorio válido y lo muestra."""
        try:
            dni = generar_dni_aleatorio()
            copiado, _trunc = self._copiar_al_portapapeles(dni)
            self.label_dni_generado.config(
                text=f"{dni}  ✓ copiado" if copiado else f"{dni}",
                fg=COLORES["exito"],
            )
        except Exception as e:
            logger.exception("Error al generar DNI: %s", e)
            messagebox.showerror(
                "Error",
                "No se pudo generar el DNI. Inténtalo de nuevo.",
            )

    def _generar_lote(self) -> None:
        """Inicia la generación de lote en un hilo secundario."""
        if self._generando_lote:
            return

        try:
            cantidad_str = self.spinbox_cantidad.get().strip()
            if not cantidad_str:
                self._mostrar_error_lote("Introduce una cantidad.")
                return

            cantidad = int(cantidad_str)
            if not LOTE_MIN <= cantidad <= LOTE_MAX:
                self._mostrar_error_lote(f"La cantidad debe estar entre {LOTE_MIN} y {LOTE_MAX}.")
                return

            self._generando_lote = True
            self._deshabilitar_boton_lote(True)
            self.label_status_lote.config(
                text="⏳ Generando...",
                fg=COLORES["primario"],
            )
            self.texto_lote.config(state=tk.NORMAL, fg=COLORES["texto_secundario"])
            self.texto_lote.delete(1.0, tk.END)
            self.texto_lote.insert(tk.END, "Generando DNIs, por favor espera...")

            def worker() -> None:
                try:
                    dnis = generar_dni_lote(cantidad)
                except Exception as e:
                    logger.exception("Error en generación de lote: %s", e)
                    msg_err = str(e)
                    self.root.after(
                        0,
                        lambda m=msg_err: self._on_lote_worker_terminado_error(m),
                    )
                else:
                    self.root.after(
                        0,
                        lambda d=dnis: self._on_lote_worker_terminado_exito(d),
                    )

            thread = threading.Thread(target=worker, daemon=True)
            thread.start()

        except ValueError as e:
            self._mostrar_error_lote(str(e))
            self._generando_lote = False
            self._deshabilitar_boton_lote(False)

    def _on_lote_worker_terminado_exito(self, dnis: list[str]) -> None:
        """
        Hilo principal: aplica resultado del lote y libera el estado de generación.

        Debe invocarse solo mediante ``root.after`` desde el worker.
        """
        self._finalizar_lote(dnis)
        self._deshabilitar_boton_lote(False)
        self._generando_lote = False

    def _on_lote_worker_terminado_error(self, mensaje: str) -> None:
        """
        Hilo principal: muestra error de lote y libera el estado de generación.

        Debe invocarse solo mediante ``root.after`` desde el worker.
        """
        self._mostrar_error_lote(f"Error: {mensaje}")
        self._deshabilitar_boton_lote(False)
        self._generando_lote = False

    def _finalizar_lote(self, dnis: list[str]) -> None:
        """Actualiza la UI con los DNIs generados (llamado desde el hilo principal)."""
        separador = self._obtener_separador_actual()
        texto = separador.join(dnis)

        self.texto_lote.config(state=tk.NORMAL, fg=COLORES["texto"])
        self.texto_lote.delete(1.0, tk.END)
        self.texto_lote.insert(tk.END, texto)

        copiado, truncado = self._copiar_al_portapapeles(texto)
        if copiado and not truncado:
            self.label_status_lote.config(
                text=f"✓ {len(dnis)} DNIs generados y copiados",
                fg=COLORES["exito"],
            )
        elif copiado and truncado:
            self.label_status_lote.config(
                text=f"✓ {len(dnis)} DNIs generados (portapapeles truncado; exporta para el lote completo)",
                fg=COLORES["exito"],
            )
        else:
            self.label_status_lote.config(
                text=f"✓ {len(dnis)} DNIs generados (exporta a archivo para copiar todo)",
                fg=COLORES["exito"],
            )

    def _deshabilitar_boton_lote(self, deshabilitar: bool) -> None:
        """Habilita o deshabilita el botón de generar lote."""
        if self._btn_generar_lote is not None:
            state = "disabled" if deshabilitar else "normal"
            self._btn_generar_lote.config(state=state)

    def _copiar_lote(self) -> None:
        """Copia el contenido actual del área de lote al portapapeles."""
        try:
            contenido = self.texto_lote.get(1.0, tk.END).strip()
            if not contenido or "aparecerán aquí" in contenido or "Generando" in contenido:
                self.label_status_lote.config(
                    text="No hay DNIs para copiar",
                    fg=COLORES["error"],
                )
                return

            copiado, truncado = self._copiar_al_portapapeles(contenido)
            if copiado and not truncado:
                self.label_status_lote.config(
                    text="✓ Lote copiado al portapapeles",
                    fg=COLORES["exito"],
                )
            elif copiado and truncado:
                self.label_status_lote.config(
                    text="✓ Copiado truncado al portapapeles. Exporta para el lote completo.",
                    fg=COLORES["exito"],
                )
            else:
                self.label_status_lote.config(
                    text="No se pudo copiar al portapapeles",
                    fg=COLORES["error"],
                )
        except Exception as e:
            logger.exception("Error al copiar lote: %s", e)
            self.label_status_lote.config(
                text="Error al copiar",
                fg=COLORES["error"],
            )

    def _exportar_dni(self) -> None:
        """Exporta el contenido del lote a un archivo."""
        try:
            contenido = self.texto_lote.get(1.0, tk.END).strip()
            if not contenido or "aparecerán aquí" in contenido or "Generando" in contenido:
                messagebox.showwarning(
                    "Sin datos",
                    "No hay DNIs para exportar. Genera un lote primero.",
                )
                return

            ruta = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[
                    ("Archivo de texto", "*.txt"),
                    ("CSV", "*.csv"),
                    ("Todos los archivos", "*.*"),
                ],
                title="Guardar DNIs",
            )

            if ruta:
                with open(ruta, "w", encoding="utf-8") as f:
                    f.write(contenido)
                self.label_status_lote.config(
                    text=f"✓ Exportado a {ruta}",
                    fg=COLORES["exito"],
                )
        except Exception as e:
            logger.exception("Error al exportar: %s", e)
            messagebox.showerror(
                "Error",
                "No se pudo guardar el archivo. Inténtalo de nuevo.",
            )

    def _mostrar_error_lote(self, mensaje: str) -> None:
        """Muestra un mensaje de error en el área de lote."""
        self.texto_lote.config(state=tk.NORMAL, fg=COLORES["error"])
        self.texto_lote.delete(1.0, tk.END)
        self.texto_lote.insert(tk.END, mensaje)
        self.label_status_lote.config(text=f"✗ {mensaje}", fg=COLORES["error"])

    def _mostrar_exito(self, label: tk.Label, mensaje: str) -> None:
        """Muestra un mensaje de éxito en verde."""
        label.config(text=mensaje, fg=COLORES["exito"])

    def _mostrar_error(self, label: tk.Label, mensaje: str) -> None:
        """Muestra un mensaje de error en rojo."""
        label.config(text=mensaje, fg=COLORES["error"])

    def run(self) -> None:
        """Inicia el bucle principal de la aplicación."""
        self.root.mainloop()


def main() -> None:
    """Punto de entrada para la aplicación gráfica."""
    app = DniApp()
    app.run()


if __name__ == "__main__":
    main()
