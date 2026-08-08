"""
JARVIS - Chat-Based AI Assistant (Modular Architecture)
Based on OpenClaw patterns with Windows focus

Architecture v2: Agent Loop with LLM tool calling
- User Input → Agent Loop → LLM decides tool(s) → Execute → Feed back → Repeat
- Shared Resources (AI, Memory, DB) used by all modules
- Tool Registry provides structured tool definitions
"""
import os
import sys
import asyncio
from colorama import Fore, Style, init

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.shared_resources import SharedResources
from src.core.tool_registry import ToolRegistry, build_all_tools
from src.core.agent_loop import AgentLoop

init(autoreset=True)


class JARVISChat:
    """
    JARVIS with agent loop architecture.

    Architecture v2:
    - User Input → AgentLoop → Groq (with tools) → tool calls → results → repeat → final text
    - ToolRegistry holds structured schemas for every capability
    - SharedResources provides AI, Memory, DB singletons
    """

    def __init__(self):
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}  JARVIS - AI Assistant (Agent Loop v2)")
        print(f"{Fore.CYAN}  Multi-step tool calling via Groq")
        print(f"{Fore.CYAN}{'='*60}\n")

        print(f"{Fore.YELLOW}🔧 Initializing agent architecture...{Style.RESET_ALL}\n")

        # Shared resources (lazy-loaded)
        self.shared = SharedResources()

        # Tool registry — register all module tools
        self.tool_registry = ToolRegistry()
        all_tools = build_all_tools()
        self.tool_registry.register_many(all_tools)

        # Agent loop — the brain
        self.agent = AgentLoop(self.shared, self.tool_registry)

        print(f"\n{Fore.GREEN}✓ All systems online!{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ Agent loop ready ({len(all_tools)} tools registered){Style.RESET_ALL}\n")

        self._show_status()

    def _show_status(self):
        """Show current system status"""
        reg_status = self.tool_registry.status()
        agent_status = self.agent.status()

        print(f"\n{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📊 System Status:{Style.RESET_ALL}")
        print(f"   Tools Registered: {reg_status['total_tools']}")
        print(f"   Tool Names: {', '.join(agent_status['tools_available'])}")
        print(f"   Conversation History: {agent_status['history_messages']} messages")

        resource_status = self.shared.status()
        print(f"\n{Fore.CYAN}💾 Resource Status:{Style.RESET_ALL}")
        print(f"   AI: {'✓ Loaded' if resource_status['ai_loaded'] else '○ Not loaded (lazy)'}")
        print(f"   Memory: {'✓ Loaded' if resource_status['memory_loaded'] else '○ Not loaded (lazy)'}")
        print(f"{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}\n")

    async def process_input(self, user_input: str, language: str = 'en'):
        """
        Process user input through the agent loop.

        Flow:
        1. Agent loop sends user input + tools to Groq
        2. LLM decides: call tool(s) or reply directly
        3. Tool results fed back to LLM for follow-up
        4. Repeat until LLM returns final text
        """
        try:
            response = await self.agent.run(user_input, language)
            return response
        except Exception as e:
            print(f"{Fore.RED}Error processing input: {e}{Style.RESET_ALL}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection"""
        spanish_words = ['crear', 'eliminar', 'carpeta', 'archivo', 'leer', 'escribir', 
                        'documento', 'en', 'del', 'la', 'el', 'está', 'qué']
        text_lower = text.lower()
        spanish_count = sum(1 for word in spanish_words if word in text_lower)
        return 'es' if spanish_count >= 2 else 'en'
    
    async def run(self):
        """Main chat loop"""
        print(f"{Fore.YELLOW}💬 Chat Mode Active — Agent Loop v2 (English/Spanish){Style.RESET_ALL}")
        print(f"{Fore.YELLOW}📝 Try these commands:{Style.RESET_ALL}")
        print(f"   • create a word file on desktop called test")
        print(f"   • read pdf document from downloads")
        print(f"   • summarize the word file thesis from documents")
        print(f"   • create an APA report called my_thesis")
        print(f"   • create folder Projects in Documents")
        print(f"   • what is the capital of France?")
        print(f"\n{Fore.YELLOW}Type 'status' to see system status{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Type 'clear' to clear conversation history{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Type 'exit' or 'quit' to stop{Style.RESET_ALL}\n")
        
        while True:
            try:
                # Get user input
                print(f"{Fore.CYAN}💬 You: {Style.RESET_ALL}", end='')
                user_input = input().strip()
                
                if not user_input:
                    continue
                
                # Check for special commands
                if user_input.lower() in ['exit', 'quit', 'salir']:
                    print(f"\n{Fore.CYAN}👋 Goodbye! Shutting down JARVIS...{Style.RESET_ALL}\n")
                    break
                
                if user_input.lower() == 'status':
                    self._show_status()
                    continue

                if user_input.lower() == 'clear':
                    self.agent.clear_history()
                    print(f"{Fore.GREEN}🗑️ Conversation history cleared.{Style.RESET_ALL}\n")
                    continue
                
                # Detect language
                language = self._detect_language(user_input)
                
                # Process input
                response = await self.process_input(user_input, language)
                
                # Display response
                print(f"\n{Fore.GREEN}🤖 JARVIS: {Style.RESET_ALL}{response}\n")
                
            except KeyboardInterrupt:
                print(f"\n\n{Fore.CYAN}👋 Goodbye! Shutting down...{Style.RESET_ALL}\n")
                break
            
            except Exception as e:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")


async def main():
    """Entry point"""
    try:
        jarvis = JARVISChat()
        await jarvis.run()
    except Exception as e:
        print(f"{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
