import gradio as gr
from manager import ResearchManager
from dotenv import load_dotenv
load_dotenv(override = True)


manager = ResearchManager()


async def run_research(query: str):
    if not query or not query.strip():
        yield "Please enter a research query."
        return

    log = ""

    async for update in manager.run(query.strip()):
        log += f"{update}\n\n"
        yield log


with gr.Blocks(title="AI Research Assistant") as demo:
    gr.Markdown("# AI Research Assistant")
    gr.Markdown(
        "Enter a topic, and the system will plan research, search the web, "
        "write a report, and send notifications."
    )

    with gr.Row():
        query_input = gr.Textbox(
            label="Research Query",
            placeholder="Example: How is AI changing investment banking?",
            lines=2,
        )

    output_box = gr.Textbox(
        label="Live Output",
        lines=25,
        max_lines=30,
        show_copy_button=True,
    )

    with gr.Row():
        run_button = gr.Button("Run Research")
        clear_button = gr.Button("Clear")

    run_button.click(
        fn=run_research,
        inputs=query_input,
        outputs=output_box,
    )

    clear_button.click(
        fn=lambda: ("", ""),
        inputs=None,
        outputs=[query_input, output_box],
    )

if __name__ == "__main__":
    demo.launch()