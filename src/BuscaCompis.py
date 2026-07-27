import itertools
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import streamlit as st

CSV_PATH = "../data/estudiantes.csv"

st.set_page_config(page_title="Buscacompis", layout="wide")


#Funciones hechas previamente
def texto_a_conjunto(texto):
    return set(texto.split(";"))


def jaccard(conjunto_a, conjunto_b):
    interseccion = conjunto_a & conjunto_b
    union = conjunto_a | conjunto_b
    if len(union) == 0:
        return 0.0
    return len(interseccion) / len(union)


def suma_ponderada(estudiante_a, estudiante_b, peso_materias=0.5, peso_horario=0.3, peso_hobbies=0.2):
    sim_materias = jaccard(estudiante_a["materias_conjunto"], estudiante_b["materias_conjunto"])
    sim_horario = jaccard(estudiante_a["horario_conjunto"], estudiante_b["horario_conjunto"])
    sim_hobbies = jaccard(estudiante_a["hobbies_conjunto"], estudiante_b["hobbies_conjunto"])
    return (peso_materias * sim_materias) + (peso_horario * sim_horario) + (peso_hobbies * sim_hobbies)


def construir_grafo(df, umbral):
    G = nx.Graph()
    for _, estudiante in df.iterrows():
        G.add_node(estudiante["id"], nombre=estudiante["nombre"])
    for i, j in itertools.combinations(df.index, 2):
        a = df.loc[i]
        b = df.loc[j]
        compatibilidad = suma_ponderada(a, b)
        if compatibilidad >= umbral:
            G.add_edge(a["id"], b["id"], weight=compatibilidad)
    return G


def recomendar_companeros(G, id_estudiante, top_n=3):
    if id_estudiante not in G:
        return []
    vecinos = G[id_estudiante]
    vecinos_ordenados = sorted(vecinos.items(), key=lambda x: x[1]["weight"], reverse=True)
    resultado = []
    for id_vecino, datos in vecinos_ordenados[:top_n]:
        nombre_vecino = G.nodes[id_vecino]["nombre"]
        resultado.append((nombre_vecino, datos["weight"]))
    return resultado


def elementos_en_comun(df, id_a, id_b):
    estudiante_a = df.loc[df["id"] == id_a].iloc[0]
    estudiante_b = df.loc[df["id"] == id_b].iloc[0]
    return {
        "materias": estudiante_a["materias_conjunto"] & estudiante_b["materias_conjunto"],
        "hobbies": estudiante_a["hobbies_conjunto"] & estudiante_b["hobbies_conjunto"],
        "horario": estudiante_a["horario_conjunto"] & estudiante_b["horario_conjunto"],
    }


def encontrar_grupos_estudio(G, tamano_minimo=3):
    cliques = list(nx.find_cliques(G))
    grupos_validos = [c for c in cliques if len(c) >= tamano_minimo]
    return grupos_validos


def verificar_simetria(G):
    for a, b in G.edges():
        if not G.has_edge(b, a):
            return False
    return True


def encontrar_no_transitividad(G, limite_ejemplos=5):
    ejemplos = []
    for b in G.nodes():
        vecinos_b = list(G.neighbors(b))
        for a, c in itertools.combinations(vecinos_b, 2):
            if not G.has_edge(a, c):
                ejemplos.append((a, b, c))
                if len(ejemplos) >= limite_ejemplos:
                    return ejemplos
    return ejemplos



def cargar_datos():
    df = pd.read_csv(CSV_PATH, encoding="latin1", skiprows=1)
    df["materias_conjunto"] = df["materias"].apply(texto_a_conjunto)
    df["hobbies_conjunto"] = df["hobbies"].apply(texto_a_conjunto)
    df["horario_conjunto"] = df["horario_disponible"].apply(texto_a_conjunto)
    return df


if "df" not in st.session_state:
    st.session_state.df = cargar_datos()

df = st.session_state.df

st.title("Buscacompis")
st.caption("Recomendación de compañeros de estudio a partir de similitud de Jaccard sobre materias, horario y hobbies.")


#Bloque para ingresar datos de nuevos estudiantes

with st.sidebar:
    st.header("Agregar estudiante")
    with st.form("form_nuevo_estudiante", clear_on_submit=True):
        nombre = st.text_input("Nombre")
        carrera = st.text_input("Carrera")
        materias = st.text_input("Materias (separadas por ;)", placeholder="Cálculo I;Programación I")
        hobbies = st.text_input("Hobbies (separados por ;)", placeholder="ajedrez;lectura")
        horario = st.text_input("Horario disponible (separado por ;)", placeholder="Lun-8am;Jue-8am")
        enviado = st.form_submit_button("Agregar")

        if enviado:
            if not (nombre and carrera and materias and hobbies and horario):
                st.warning("Completa todos los campos antes de agregar.")
            else:
                nuevo_id = int(df["id"].max()) + 1 if len(df) else 1
                nueva_fila = {
                    "id": nuevo_id,
                    "nombre": nombre,
                    "carrera": carrera,
                    "materias": materias,
                    "hobbies": hobbies,
                    "horario_disponible": horario,
                    "materias_conjunto": texto_a_conjunto(materias),
                    "hobbies_conjunto": texto_a_conjunto(hobbies),
                    "horario_conjunto": texto_a_conjunto(horario),
                }
                st.session_state.df = pd.concat(
                    [df, pd.DataFrame([nueva_fila])], ignore_index=True
                )
                st.success(f"{nombre} agregado (id={nuevo_id}).")
                st.rerun()

    
#Bloque para cambiar el umbral
    st.divider()
    st.header("Umbral de compatibilidad")
    umbral = st.slider(
        "Compatibilidad mínima para conectar dos estudiantes",
        min_value=0.0, max_value=1.0, value=0.5, step=0.1,
    )

#Botón para guardar los cambios en el CSv
    st.divider()
    if st.button("Guardar cambios en el CSV"):
        columnas_csv = ["id", "nombre", "carrera", "materias", "hobbies", "horario_disponible"]
        with open(CSV_PATH, "w", encoding="latin1", newline="") as f:
            f.write("sep=,\n")
        df[columnas_csv].to_csv(CSV_PATH, mode="a", index=False, encoding="latin1")
        st.success("CSV actualizado.")



#Bloque donde se muestra el grafo
df = st.session_state.df
G = construir_grafo(df, umbral)

col_grafo, col_datos = st.columns([2, 1])

with col_grafo:
    st.subheader(f"Grafo de compatibilidad (umbral = {umbral:.2f})")

    n_nodos = G.number_of_nodes()
    n_aristas = G.number_of_edges()
    aislados = list(nx.isolates(G))
    densidad = nx.density(G) if n_nodos > 1 else 0.0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Estudiantes", n_nodos)
    m2.metric("Conexiones", n_aristas)
    m3.metric("Densidad", f"{densidad:.3f}")
    m4.metric("Aislados", len(aislados))

    fig, ax = plt.subplots(figsize=(8, 6))
    pos = nx.spring_layout(G, seed=42, k=1.7, iterations=100)
    etiquetas = nx.get_node_attributes(G, "nombre")
    pesos = [G[u][v]["weight"] * 4 for u, v in G.edges()]

    nx.draw_networkx_nodes(G, pos, node_color="lightblue", node_size=800, ax=ax)
    nx.draw_networkx_labels(G, pos, labels=etiquetas, font_size=7, ax=ax)
    nx.draw_networkx_edges(G, pos, width=pesos, alpha=0.6, ax=ax)
    ax.axis("off")
    st.pyplot(fig)


#Bloque de análisis complementario sobre el grafo
with col_datos:
    st.subheader("Estudiantes")
    st.dataframe(df[["id", "nombre", "carrera"]], hide_index=True, use_container_width=True)

    st.subheader("Componentes conexas")
    componentes = list(nx.connected_components(G))
    for i, comp in enumerate(componentes, start=1):
        nombres = [G.nodes[id_est]["nombre"] for id_est in comp]
        st.write(f"**Componente {i}** ({len(nombres)}): {', '.join(nombres)}")

    st.subheader("Grado de nodo")
    grados = dict(G.degree())
    grados_ordenados = sorted(grados.items(), key=lambda x: x[1], reverse=True)
    tabla_grados = pd.DataFrame(
        [(G.nodes[id_est]["nombre"], grado) for id_est, grado in grados_ordenados],
        columns=["Estudiante", "Conexiones"],
    )
    st.dataframe(tabla_grados, hide_index=True, use_container_width=True)


#Bloque para la recomendación a un estudante

st.divider()
st.subheader("Recomendación de compañeros")

opciones = dict(zip(df["nombre"], df["id"]))
nombre_sel = st.selectbox("Elige un estudiante", list(opciones.keys()))
id_sel = opciones[nombre_sel]

recomendaciones = recomendar_companeros(G, id_sel, top_n=3)

if recomendaciones:
    for nombre_vecino, compatibilidad in recomendaciones:
        id_vecino = int(df.loc[df["nombre"] == nombre_vecino, "id"].values[0])
        comunes = elementos_en_comun(df, id_sel, id_vecino)
        with st.expander(f"{nombre_vecino} — compatibilidad {compatibilidad:.3f}"):
            st.write("**Materias en común:**", ", ".join(comunes["materias"]) or "ninguna")
            st.write("**Hobbies en común:**", ", ".join(comunes["hobbies"]) or "ninguno")
            st.write("**Horario en común:**", ", ".join(comunes["horario"]) or "ninguno")
else:
    st.info(f"{nombre_sel} no tiene compañeros compatibles con el umbral actual.")


#Bloque donde se muestran los posibles grupos de estudia usando cliques

st.divider()
st.subheader("Grupos de estudio")
st.caption("Un grupo de estudio es un clique: un subconjunto de estudiantes donde todos son mutuamente compatibles.")

tamano_minimo = st.number_input("Tamaño mínimo del grupo", min_value=2, max_value=10, value=3, step=1)
grupos = encontrar_grupos_estudio(G, tamano_minimo=tamano_minimo)

if grupos:
    for i, grupo in enumerate(grupos, start=1):
        nombres = [G.nodes[id_est]["nombre"] for id_est in grupo]
        st.write(f"**Grupo {i}** ({len(nombres)} estudiantes): {', '.join(nombres)}")
else:
    st.info(f"No se encontraron grupos de {tamano_minimo} o más estudiantes mutuamente compatibles con el umbral actual.")


#Bloque de análisis de la relación entre dos estudiantes

st.divider()
st.subheader("Propiedades de la relación")
st.caption("¿La relación de compatibilidad es simétrica? ¿Es transitiva?")

col_sim, col_trans = st.columns(2)

with col_sim:
    es_simetrica = verificar_simetria(G)
    st.metric("¿Es simétrica?", "Sí" if es_simetrica else "No")

with col_trans:
    ejemplos_no_transitivos = encontrar_no_transitividad(G, limite_ejemplos=5)
    st.metric("¿Es transitiva?", "No" if ejemplos_no_transitivos else "Sí (sin contraejemplos hallados)")

if ejemplos_no_transitivos:
    st.write("**Ejemplos donde A–B y B–C son compatibles, pero A–C no:**")
    for a, b, c in ejemplos_no_transitivos:
        nombre_a = G.nodes[a]["nombre"]
        nombre_b = G.nodes[b]["nombre"]
        nombre_c = G.nodes[c]["nombre"]
        st.write(f"- {nombre_a} — {nombre_b} — {nombre_c}  (pero {nombre_a} y {nombre_c} no son compatibles)")
