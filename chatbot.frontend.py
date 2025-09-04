import streamlit as st
from chatbot_backend import chatbot, extract_unique_threads, remove_specific_thread
from langchain_core.messages import HumanMessage,AIMessage
from utilities import generate_unique_thread_id

def reset_chat():
    st.session_state["thread_id"] = generate_unique_thread_id()
    add_thread_to_thread_list(st.session_state['thread_id'])
    st.session_state["message_history"] = []


def add_thread_to_thread_list(thread_id):
    if thread_id not in st.session_state["thread_list"]:
        st.session_state["thread_list"].append(thread_id)

   
def load_previous_conversation_history(thread_id):
    state = chatbot.get_state(
                config={'configurable': {'thread_id': thread_id}}
            )
    # Check if messages key exists in state values, return empty list if not
    return state.values.get('messages', [])

#------------------------------------   Session Init Setup ------------------------------------#

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if "thread_list" not in st.session_state:
    st.session_state['thread_list'] = extract_unique_threads()

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_unique_thread_id()

add_thread_to_thread_list(st.session_state['thread_id'])

# ---------------------------------------- Side bar UI -------------------------------------#

st.sidebar.title("My Conversations")

if st.sidebar.button(label="New Chat"):
    reset_chat()

for thread_id in st.session_state["thread_list"][::-1]:
    messages = load_previous_conversation_history(thread_id)
    buttonTitle = messages[0].content[:30] if len(messages) > 0 else f"Current Chat Window {thread_id}"

    # Sidebar row with 2 columns: "open" button and "delete" button
    with st.sidebar.container():
        col1, col2 = st.columns([4, 1])  # adjust ratio for spacing
        with col1:
            if st.button(str(buttonTitle), key=f"open_{thread_id}"):
                st.session_state["thread_id"] = thread_id

                sanitized_messages = []
                for msg in messages:
                    role = "user" if isinstance(msg, HumanMessage) else "assistant"
                    sanitized_messages.append({'role': role, 'content': msg.content})

                st.session_state['message_history'] = sanitized_messages

        with col2:
            if st.button("🗑", key=f"delete_{thread_id}"):  # trash icon as label
                # remove thread from db first
                remove_specific_thread(thread_id)
                st.session_state["thread_list"].remove(thread_id)
                st.success(f"Deleted thread {thread_id}")
                st.rerun()
#------------------------------ loading the conversation history ----------------------------#
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])


# ------------------------------------------Screen  UI ---------------------------------------- #
user_input = st.chat_input("Type here...")


if user_input:
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message("user"):
        st.text(user_input)

    
    with st.chat_message("assistant"):

        def ai_stream():
            for message_chunk, metadata in  chatbot.stream(
                {"messages": [HumanMessage(content= user_input)]},
                config={
                    'configurable': {'thread_id': st.session_state['thread_id']},
                    "metadata":{
                        "thread_id": st.session_state["thread_id"]
                    },
                    "run_name":"Chat Turn"
                },
                stream_mode="messages"
            ):
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        # ai_message = st.write(
        #     message_chunk.content for message_chunk, metadata in  chatbot.stream(
        #         {"messages":[HumanMessage(content=user_input)]},
        #         config= {'configurable': {'thread_id': st.session_state['thread_id']}},
        #         stream_mode='messages'
        #     )
        # )

        ai_message = st.write_stream(ai_stream())

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})