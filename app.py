import gradio as gr
from query import ask


def handle_query(question: str):
    if not question.strip():
        return "Please enter a question.", ""

    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources


with gr.Blocks(title="GSU Unofficial Guide") as demo:
    gr.Markdown(
        "## GSU Unofficial Guide\n"
        "Ask anything about CS courses, professors, housing, dining, or campus life at Georgia State University. "
        "All answers are drawn from real student reviews and community posts."
    )

    with gr.Row():
        with gr.Column(scale=3):
            inp = gr.Textbox(
                label="Your question",
                placeholder='e.g. "Is the housing lottery actually random?" or "Which CS professor gives the most useful feedback?"',
                lines=2,
            )
            btn = gr.Button("Ask", variant="primary")

    with gr.Row():
        with gr.Column(scale=3):
            answer_box = gr.Textbox(label="Answer", lines=10, interactive=False)
        with gr.Column(scale=1):
            sources_box = gr.Textbox(label="Retrieved from", lines=10, interactive=False)

    btn.click(handle_query, inputs=inp, outputs=[answer_box, sources_box])
    inp.submit(handle_query, inputs=inp, outputs=[answer_box, sources_box])

    gr.Examples(
        examples=[
            ["What do students say about Dr. Prasad's office hours for OS?"],
            ["Is the GSU housing lottery actually random?"],
            ["Which dining hall is open the latest at GSU?"],
            ["What GPA do I need to keep the HOPE Scholarship?"],
            ["What is the grading breakdown for CS 4320 with Dr. Aluru?"],
            ["What is the best restaurant in downtown Chicago?"],
        ],
        inputs=inp,
    )


if __name__ == "__main__":
    demo.launch()
