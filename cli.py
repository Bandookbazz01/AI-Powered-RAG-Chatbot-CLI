import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.chat_engine import generate_response
from app.database import initialize_knowledge_base

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

def main():
    console.print(Panel.fit("[bold cyan]🤖 Welcome to the Advanced AI Chatbot CLI![/]\nType 'exit' or 'quit' to end the conversation.\nType 'clear' to start a new session.", title="Chatbot", border_style="cyan"))

    try:
        console.print("[blue]Loading knowledge base...[/]")
        initialize_knowledge_base()
    except Exception as e:
        console.print(f"[yellow]⚠️  Knowledge base initialization warning: {str(e)}[/]")

    user_id = Prompt.ask("[bold]Enter your Username / Session ID[/]", default="default_user").strip()
    
    console.print(f"\n[bold green]👋 Welcome, {user_id}! Let's chat.[/]\n")

    while True:
        try:
            user_input = Prompt.ask("\n[bold blue]You[/]")
            user_input = user_input.strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit']:
                console.print("\n[bold green]Bot: Goodbye! 👋[/]")
                break
            
            if user_input.lower() == 'clear':
                user_id = Prompt.ask("[bold]Enter new Username / Session ID[/]", default="default_user").strip()
                console.print(f"[bold green]✅ Session cleared. Welcome, {user_id}![/]\n")
                continue
                
            if user_input.startswith('/pdf '):
                pdf_path = user_input.split('/pdf ')[1].strip()
                from app.database import process_and_add_pdf
                console.print("[bold yellow]Processing PDF...[/]")
                process_and_add_pdf(pdf_path)
                continue
                
            if user_input.startswith('/search '):
                query = user_input.split('/search ')[1].strip()
                from app.tools import search_web
                console.print("[bold yellow]Searching the web...[/]")
                web_results = search_web(query)
                user_input = f"Based on these web search results, answer the question '{query}'. Results: {web_results}"
                
            if user_input.lower() == '/voice':
                # Toggle voice logic could go here
                console.print("[bold yellow]Voice mode toggle is ready. Implement microphone here if needed![/]")
                from app.voice import listen_to_mic
                spoken = listen_to_mic()
                if spoken:
                    console.print(f"[bold cyan]You (Mic):[/] {spoken}")
                    user_input = spoken
                else:
                    continue

            console.print("[bold magenta]Bot is thinking...[/]", end="\r")
            response = generate_response(user_id=user_id, message=user_input)
            
            # Print the markdown response cleanly!
            console.print(" " * 20, end="\r") # Clear the 'thinking' text
            console.print("[bold magenta]Bot:[/]")
            md = Markdown(response)
            console.print(md)
            
            # Speak if needed (uncomment to always speak)
            # from app.voice import speak_text
            # speak_text(response)
            
        except KeyboardInterrupt:
            console.print("\n[bold green]Bot: Goodbye! 👋[/]")
            break
        except Exception as e:
            console.print(f"\n[bold red]❌ [Error] {str(e)}[/]\n")

if __name__ == "__main__":
    main()