import streamlit as st
import json
import os
from mistralai import Mistral

# Configurazione della pagina
st.set_page_config(page_title="Svuota Frigo Smart", page_icon="🥗")

# Legge la chiave API dalle variabili d'ambiente di Render
API_KEY = os.environ.get("yTvmRtdl6rPPRHfFD412ECb7Vaf04C8a")

# Interfaccia Utente (Nessun riferimento all'IA)
st.title("🥗 Svuota Frigo Smart")
st.write("Inserisci gli ingredienti disponibili nella tua dispensa per trovare le ricette più adatte.")

ingredienti_input = st.text_input(
    "Ingredienti disponibili (separati da virgola):", 
    placeholder="es. uova, zucchine, parmigiano"
)

if st.button("Cerca Ricette"):
    if not ingredienti_input:
        st.warning("Inserisci almeno un ingrediente!")
    elif not API_KEY:
        st.error("Chiave API non configurata nelle impostazioni del server.")
    else:
        client = Mistral(api_key=API_KEY)

        with st.spinner("🔍 Ricerca delle ricette migliori nel database..."):
            try:
                system_prompt = """
                Sei un database culinario anti-spreco.
                Restituisci ESCLUSIVAMENTE un oggetto JSON valido in italiano con la seguente struttura:
                {
                  "ricette": [
                    {
                      "titolo": "Nome della ricetta",
                      "tempo": "Tempo di preparazione",
                      "difficolta": "Facile/Media/Difficile",
                      "ingredientiMancanti": ["ingrediente1", "ingrediente2"],
                      "passaggi": ["Passo 1...", "Passo 2..."]
                    }
                  ]
                }
                Non aggiungere alcun testo prima o dopo l'oggetto JSON.
                """

                response = client.chat.complete(
                    model="mistral-small-latest",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Crea 2 ricette usando principalmente questi ingredienti: {ingredienti_input}"}
                    ],
                    response_format={"type": "json_object"}
                )

                data = json.loads(response.choices[0].message.content)

                for ricetta in data.get("ricette", []):
                    st.divider()
                    st.header(ricetta["titolo"])
                    
                    col1, col2 = st.columns(2)
                    col1.write(f"⏱️ **Tempo:** {ricetta['tempo']}")
                    col2.write(f"📊 **Difficoltà:** {ricetta['difficolta']}")
                    
                    mancanti = ", ".join(ricetta["ingredientiMancanti"]) if ricetta["ingredientiMancanti"] else "Nessuno!"
                    st.write(f"🛒 **Ingredienti extra consigliati:** {mancanti}")
                    
                    st.subheader("Preparazione:")
                    for i, passaggio in enumerate(ricetta["passaggi"], 1):
                        st.write(f"{i}. {passaggio}")

            except Exception as e:
                st.error("Impossibile recuperare le ricette al momento. Riprova tra poco.")