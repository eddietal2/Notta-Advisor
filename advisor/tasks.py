from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import os
import sys
from pathlib import Path

# Add the project root to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from google_llm_init import initialize_llm
from llama_index.core import VectorStoreIndex, load_index_from_storage
from llama_index.core.storage import StorageContext
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import FunctionAgent
import yfinance as yf
from advisor.models import Subscription

@shared_task
def run_financial_analysis():
    """
    Scheduled task to run financial analysis for all active subscribers.
    """
    # Initialize LLM
    llm = initialize_llm()

    # Load "The Intelligent Investor" index
    storage_context = StorageContext.from_defaults(persist_dir="./storage/intelligent_investor")
    investor_index = load_index_from_storage(storage_context)
    investor_engine = investor_index.as_query_engine(llm=llm)

    # Create tool for investor wisdom
    investor_tool = QueryEngineTool(
        query_engine=investor_engine,
        metadata=ToolMetadata(
            name="investor_wisdom",
            description="Provides wisdom from 'The Intelligent Investor' by Benjamin Graham"
        )
    )

    # Tool for market data
    def get_market_data(ticker: str) -> str:
        stock = yf.Ticker(ticker)
        info = stock.info
        return f"Company: {info.get('longName', 'N/A')}\nSector: {info.get('sector', 'N/A')}\nMarket Cap: {info.get('marketCap', 'N/A')}\nPE Ratio: {info.get('trailingPE', 'N/A')}"

    market_tool = QueryEngineTool(
        query_engine=lambda q: get_market_data(q),
        metadata=ToolMetadata(
            name="market_data",
            description="Fetches real-time market data for a given stock ticker"
        )
    )

    # Create agent
    agent = FunctionAgent.from_tools([investor_tool, market_tool], llm=llm)

    # Load system prompt
    with open("system_prompt.txt", "r") as f:
        system_prompt = f.read()

    # For each subscriber, generate and send analysis
    subscriptions = Subscription.objects.filter(is_active=True)
    for sub in subscriptions:
        # Customize prompt based on preferences
        prompt = f"{system_prompt}\nUser preferences: {sub.preferences}"
        response = agent.chat(prompt)
        analysis = str(response)

        # Send email
        send_mail(
            'Your Weekly Financial Analysis',
            analysis,
            settings.EMAIL_HOST_USER,
            [sub.email],
            fail_silently=False,
        )