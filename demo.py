import streamlit as st
import openai
import configs
import pyaudio, wave
import os


def intro():
    st.write("# Welcome to ChatGPT and Whisper App demo! 👋")
    st.sidebar.success("Select a demo above.")

    st.markdown(
        """
        This is an open-source app that demonstrates the capabilities of the OpenAI's API.

        **👈 Select a demo from the dropdown on the left** to see some examples of the API's potential.

        ### Here are some useful links

        - Check out [API Reference](https://platform.openai.com/docs/api-reference/introduction)
        - Jump into the [documentation](https://platform.openai.com/docs/introduction/overview)
        - Check out the guides for different tasks [here](https://platform.openai.com/docs/guides/completion)

        ### AI Bites
        - [YouTube](https://www.youtube.com/@aibites)
        - [Twitter](https://twitter.com/ai_bites)
        - [Github](https://github.com/ai-bites)
        - [Patreon](https://www.patreon.com/ai_bites)
    """
    )


def chat_completion():
    st.markdown(f"# {list(page_names_to_funcs.keys())[1]}")
    st.write(
        """
        This page illustrates the possibilities of the Chat Completion API. Chat completion is different from completion in that they take a series of messages 
        and make multi-turn conversations. Set the different paramters, give ChatGPT a prompt and enjoy the response!
"""
    )

    with st.form("system_form", clear_on_submit=True):
        topic = st.text_input("Initiate the chat system with a topic")
        system_msg_submitted = st.form_submit_button("Submit")
    if system_msg_submitted:
        if not topic:
            st.error("Please enter a topic to proceed!")
        else:
            st.info("Done! I am all set to chat with you!")

        configs.MESSAGES.append({"role": "system", "content": topic})

    with st.form("chat_form", clear_on_submit=True):
        input_message = st.text_input("How can I help?")
        temperature = st.slider(
            "Temperature", min_value=0.0, max_value=2.0, value=1.0, step=0.1
        )
        max_tokens = st.slider(
            "Max Tokens", min_value=5, max_value=2048, value=16, step=1
        )
        chat_submitted = st.form_submit_button("Chat")

        if chat_submitted:
            configs.MESSAGES.append({"role": "user", "content": input_message})

            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=configs.MESSAGES,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            configs.MESSAGES.append(completion["choices"][0]["message"])

        print(f"message in the end is {configs.MESSAGES}")

    with st.form("display_form"):
        for message in configs.MESSAGES:
            st.info(message["role"] + ": " + message["content"])
        refresh = st.form_submit_button("Start a New Topic / Refresh")
        if refresh:
            configs.MESSAGES = list()


def completion():
    import streamlit as st
    import configs

    st.markdown(f"# {list(page_names_to_funcs.keys())[1]}")
    st.write(
        """
        This page illustrates the possibilities of the Completion API. Set the different paramters, give ChatGPT a prompt and enjoy the response!
"""
    )
    with st.form("my_form"):
        model = st.selectbox("Select a Model", options=configs.MODEL_NAMES)
        prompt = st.text_area("Prompt")
        max_tokens = st.slider("Max Tokens")
        temperature = st.slider(
            "Temperature", min_value=0, max_value=5, value=1, step=1
        )
        top_p = st.slider(
            "Top P", min_value=0.0, max_value=1.0, value=0.0, step=0.1
        )
        num_completions = st.slider("Number of Completions")
        echo = st.checkbox("Echo back the Prompt")
        submitted = st.form_submit_button("Submit")

    if submitted:
        response = openai.Completion.create(
            model=model,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            n=num_completions,
            echo=echo,
            top_p=top_p,
        )
        st.info(response["choices"][0]["text"])
        print(f"num_completions is {num_completions} and prompt is {prompt}")

    st.button("Restart")


def text_editing():
    import streamlit as st
    import configs

    st.markdown(f"# {list(page_names_to_funcs.keys())[3]}")
    st.write(
        """
        This page illustrates the possibilities for correcting any given input text or code. Set the different paramters, give ChatGPT a prompt and enjoy the response showing the corrected text or code!
"""
    )

    with st.form("my_form"):
        model = st.selectbox("Select a Model", options=configs.EDIT_MODELS)
        input = st.text_area("Input")
        instruction = st.text_input("Instruction")
        # num_edits = st.slider(
        #     "Number of Edits to generate", value=1, min_value=1, max_value=5
        # )
        submitted = st.form_submit_button("Submit")
    if submitted:
        response = openai.Edit.create(
            model=model, input=input, instruction=instruction,  # n=num_edits
        )
        st.info(response["choices"][0]["text"])
    st.button("Restart")


def images():
    st.markdown(f"# {list(page_names_to_funcs.keys())[4]}")
    st.write(
        """
        This page illustrates the possibilities of the Dall.E API. Set the different paramters, give Dall.E a prompt and watch images generated as per your instruction!
"""
    )
    with st.form("my_form"):
        # image = st.file_uploader("Upload an image to edit", type="png")
        prompt = st.text_area("Prompt")
        num_imgs = st.slider(
            "Number of Images to Generate", min_value=1, max_value=5, value=1
        )
        size = st.select_slider(
            "Select output image size",
            options=["256x256", "512x512", "1024x1024"],
        )
        submitted = st.form_submit_button("Submit")

        if submitted:
            # generate an image
            response = openai.Image.create(
                prompt=prompt, n=num_imgs, size=size
            )
            for data in response["data"]:
                st.image(
                    data["url"], width=int(size.split("x")[0]),
                )
    st.button("Restart")


def record_audio(task):
    p = pyaudio.PyAudio()
    stream = p.open(
        format=configs.FORMAT,
        channels=configs.CHANNELS,
        rate=configs.RATE,
        input=True,
        frames_per_buffer=configs.CHUNK,
    )
    print("Start recording")

    frames = list()
    seconds = configs.SPEECH_RECORD_TIME
    for i in range(0, int(configs.RATE / configs.CHUNK * seconds)):
        data = stream.read(configs.CHUNK)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    p.terminate()

    # dump everything in a wave file
    if task == "Translate":
        print("translating")
        wf = wave.open(configs.AUDIO_TRANSLATE_FNAME, "wb")
    else:
        print("transcribing")
        wf = wave.open(configs.AUDIO_TRANSCRIBE_FNAME, "wb")

    wf.setnchannels(configs.CHANNELS)
    wf.setsampwidth(p.get_sample_size(configs.FORMAT))
    wf.setframerate(configs.RATE)
    wf.writeframes(b"".join(frames))
    wf.close()
    print("done recording")


def audio():
    st.markdown(f"# {list(page_names_to_funcs.keys())[5]}")
    st.write(
        """
        This page illustrates the possibilities of the Whisper API. Set the different parameters, talk to Whisper and watch the Whisper transcribe or translate what you say!
"""
    )
    with st.form("click_to_talk_form"):
        task = st.selectbox("Select the Task", ["Transcribe", "Translate"])
        print(f"task is {task}")
        click_to_talk = st.form_submit_button(
            "Click to Talk", on_click=record_audio, args=(task,)
        )
        if click_to_talk:
            if task == "Transcribe":
                st.audio(configs.AUDIO_TRANSCRIBE_FNAME)
            else:
                st.audio(configs.AUDIO_TRANSLATE_FNAME)

    with st.form("audio_submit_form"):
        model = st.selectbox("Select the model", ["whisper-1"])
        prompt = st.text_input("Prompt (optional)")
        temperature = st.slider(
            "Temperature", min_value=0.0, max_value=1.0, value=0.0, step=0.1
        )
        submitted = st.form_submit_button("Submit")
        if submitted:
            if task == "Transcribe":
                try:
                    audio_content = open(configs.AUDIO_TRANSCRIBE_FNAME, "rb")
                except:
                    st.info("Please talk something before transcribing!")
                    return
                response = openai.Audio.transcribe(
                    model,
                    audio_content,
                    prompt=prompt,
                    temperature=temperature,
                )
            if task == "Translate":
                try:
                    audio_content = open(configs.AUDIO_TRANSLATE_FNAME, "rb")
                except:
                    st.info("Please talk something before transcribing!")
                    return
                response = openai.Audio.translate(
                    model,
                    audio_content,
                    prompt=prompt,
                    temperature=temperature,
                )

            st.info(response["text"])
    restarted = st.button("Restart")
    if restarted:
        if os.path.exists(configs.AUDIO_TRANSCRIBE_FNAME):
            os.remove(configs.AUDIO_TRANSCRIBE_FNAME)
        if os.path.exists(configs.AUDIO_TRANSLATE_FNAME):
            os.remove(configs.AUDIO_TRANSLATE_FNAME)


# Page Starts here
openai.api_key = configs.OPENAI_AUTH_KEY

page_names_to_funcs = {
    "Home": intro,
    "Completion": completion,
    "Chat Completion": chat_completion,
    "Text Editing": text_editing,
    "Image": images,
    "Audio": audio,
}

demo_name = st.sidebar.selectbox("Choose a demo", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]()
