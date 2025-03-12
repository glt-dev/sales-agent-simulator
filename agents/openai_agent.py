import openai, os, json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

ASSISTANT_ID = "asst_udnUtmXgsLIM3WFfKDTlQWcU"

sessions = {}


def initiate_chat(sales_person, archetype, business_line):
    thread = openai.beta.threads.create()
    session_id = thread.id
    sessions[session_id] = {
        "sales_person": sales_person,
        "archetype": archetype,
        "business_line": business_line,
        "date": datetime.now().isoformat(),
        "thread_id": thread.id,
        "chat_log": []
    }
    print(f"[INITIATE CHAT] Session initiated with thread_id: {thread.id}")

    # Send initial trigger message to assistant
    initial_message = "Ciao, come posso aiutarti?"
    reply = send_message(session_id, initial_message)
    return session_id, reply



def send_message(session_id, message):
    thread_id = sessions[session_id]["thread_id"]
    print(f"[SEND MESSAGE] Sending message to thread_id: {thread_id}")

    openai.beta.threads.messages.create(thread_id=thread_id, role="user", content=message)

    run = openai.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=ASSISTANT_ID,
        instructions=f"Sei un cliente '{sessions[session_id]['archetype']}' interessato al servizio '{sessions[session_id]['business_line']}'."
    )

    print(f"[RUN CREATED] Run ID: {run.id}, Status: {run.status}")

    while run.status in ["queued", "in_progress"]:
        run = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        print(f"[RUN STATUS] {run.status}")

    messages = openai.beta.threads.messages.list(thread_id=thread_id)
    reply = messages.data[0].content[0].text.value

    sessions[session_id]["chat_log"].append({"role": "sales", "message": message})
    sessions[session_id]["chat_log"].append({"role": "agent", "message": reply})

    print(f"[REPLY RECEIVED] {reply}")

    return reply


def end_chat(session_id):
    session = sessions.get(session_id, {})
    chat_log = session.get("chat_log", [])

    prompt_feedback = (
        f"Sei un esperto coach di vendita. Dai un feedback costruttivo al venditore basandoti sulla conversazione "
        f"con l'archetipo '{session.get('archetype')}' nel prodotto '{session.get('business_line')}'."
    )

    print(f"[GENERATING FEEDBACK] Prompt: {prompt_feedback}")

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt_feedback},
            {"role": "user", "content": json.dumps(chat_log)}
        ]
    )

    feedback = response.choices[0].message.content

    session_data = {
        "sales_person": session.get("sales_person"),
        "archetype": session.get("archetype"),
        "business_line": session.get("business_line"),
        "date": session.get("date"),
        "chat_log": chat_log,
        "feedback": feedback
    }

    # Make sure the directory exists
    log_dir = 'data/chat_logs/'
    os.makedirs(log_dir, exist_ok=True)

    with open(f'{log_dir}{session_id}.json', 'w', encoding='utf-8') as f:
        json.dump(session_data, f, ensure_ascii=False, indent=4)

    print(f"[SESSION ENDED] Feedback saved for session: {session_id}")

    return {"feedback": feedback}
