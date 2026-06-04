from langchain_openai import OpenAIEmbeddings
from rag.text_chunking.main import text_chunking
from dotenv import load_dotenv

load_dotenv()

def generate_embeddings_for_chunks(chunks:list):
    '''Generates embeddings for a list of text chunks using openai text-embedding-3-small model.'''

    # 4. Initialize the embedding model
    embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

    text_to_embed = [chunk.page_content for chunk in chunks]

    # 5. Generate embeddings for all text chunks at once
    chunk_embeddings = embedding_model.embed_documents(text_to_embed)

    return chunk_embeddings
    # # Verify the output structure
    # print(f"Generated {len(chunk_embeddings)} embedding vectors.")
    # print(f"Vector size (dimensions): {len(chunk_embeddings[0])}")
    # print(chunk_embeddings)

if __name__ == "__main__":
    markdown_document = """
    # Multi-Agent Corporate Governance & Document Analytics Engine

## Project Overview

The Multi-Agent Corporate Governance & Document Analytics Engine is an enterprise-grade AI platform designed to automate the analysis of financial, legal, compliance, ESG (Environmental, Social, and Governance), sustainability, audit, and regulatory documents. Unlike traditional "Chat with PDF" applications, this platform operates as a fully autonomous multi-agent intelligence system where specialized AI agents collaborate, verify each other's work, perform document retrieval, audit findings, and generate executive-level governance reports. The platform is designed to simulate the workflow used by global consulting and audit firms such as:

- Deloitte
- PwC
- EY
- KPMG
- McKinsey
- BCG
  The system enables organizations to upload thousands of pages of reports, filings, and compliance documents and receive verified, source-backed insights through an interactive enterprise dashboard.

# Business Problem

Organizations generate massive amounts of documentation:

- Annual Reports
- Financial Statements
- Sustainability Reports
- ESG Disclosures
- SEC Filings
- Risk Assessments
- Legal Contracts
- Compliance Reports
- Internal Audit Documents
  Reviewing these documents manually requires significant time, expertise, and resources.

Traditional RAG systems can answer questions but often suffer from:

- Hallucinations
- Missing evidence
- Lack of verification
- Poor auditability
- Limited reasoning capabilities
  This platform addresses these issues by introducing a coordinated network of specialized AI agents that perform extraction, retrieval, auditing, validation, and criticism before producing a final report.

# System Architecture

User │ ▼ Next.js Enterprise UI │ ▼ NestJS Gateway │ ▼ FastAPI API │ ▼ File Ingestion Service │ ▼ Redis Queue │ ▼ BullMQ │ ▼ LangGraph Agent Engine │ ┌───────────────────┼───────────────────┐ ▼ ▼ ▼ Router Agent Extraction Agent Search Agent ▼ ▼ ▼ Audit Agent Verification Agent ESG Agent

└───────────────────┼───────────────────┘ ▼ Critic Agent ▼ Final Report ▼ PostgreSQL + pgvector/Pinecone

# Technology Stack

## Package Management

### UV (Astral)

The project uses UV as the primary package manager for Python. Benefits:

- Extremely fast dependency resolution

- Faster environment creation

- Reproducible builds

- Better developer experience than pip
  Responsibilities:

- Dependency installation

- Virtual environment management

- Lock file generation

- Build reproducibility


# Frontend Architecture

## Next.js + React + TypeScript

The frontend acts as an enterprise governance dashboard.

Responsibilities:

- User Authentication
- Document Upload
- Agent Monitoring
- Report Visualization
- Analytics Dashboards
- Source Verification
- Organization Management

## Login & Authentication Module

Enterprise-grade authentication system supporting:

**Features**

- JWT Authentication
- Refresh Tokens
- RBAC (Role-Based Access Control)
- Multi-Tenant Organizations

### User Roles

### Compliance Officer

Responsible for:

- Regulatory compliance monitoring
- Governance review
- Policy enforcement

### Financial Auditor

Responsible for:

- Financial statement validation
- Revenue verification
- Risk assessment

### Legal Analyst

Responsible for:

- Contract review
- Legal clause extraction
- Regulatory interpretation

### ESG Reviewer

Responsible for:

- Sustainability reporting
- Carbon emissions analysis
- Climate risk evaluation

## Dashboard Module

The central command center of the platform.

**Displays** **Uploaded Documents**

Annual Report.pdf SEC Filing.pdf Sustainability Report.xlsx

### Processing Status

Queued Running Completed Failed

### Active Agent Jobs

Extraction Agent Audit Agent Search Agent Critic Agent

### Analytics Widgets

- Document Statistics
- Agent Performance
- Processing Costs
- Token Usage
- Success Rates

## Upload Center

Supports enterprise document ingestion.

### Supported Formats

- PDF
- XLSX
- CSV
- DOCX
  **Workflow**

Upload ↓ Validation ↓ Storage ↓ Queue Creation ↓ Processing Start

Features:

- Drag and Drop Upload
- Multiple File Upload
- Progress Tracking
- File Validation
- Retry Support

# Backend Architecture

## FastAPI

FastAPI serves as the AI orchestration backend. Responsibilities:

- API endpoints

- Authentication

- Agent execution

- Workflow management

- Queue creation

- Database interactions
  **Benefits**

- Asynchronous architecture

- High throughput

- Excellent LLM integration

- Fast performance


## NestJS Gateway

Acts as an enterprise gateway layer. Responsibilities:

- API aggregation

- Authentication middleware

- Organization routing

- Request logging

- Rate limiting
  Benefits:

- Enterprise scalability

- Microservice readiness

- Better separation of concerns


# Background Processing Layer

## Redis

Redis acts as:

- Message Broker
- Queue Backend
- Cache Layer
- Session Store

## BullMQ

BullMQ manages long-running AI tasks.

### Why BullMQ?

Processing large reports may require:

- OCR

- Table extraction

- Embedding generation

- Multi-agent analysis
  These tasks may take minutes. BullMQ ensures:

- Non-blocking processing

- Retries

- Job recovery

- Fault tolerance


## Job Lifecycle

Job Created ↓ Queued ↓ Worker Assigned ↓ Processing ↓ Completed

Example:

Job #1981 Status: Queued Progress: 72% Estimated Time: 2 Minutes

# Document Processing Pipeline

## Stage 1: File Ingestion Agent

Responsible for understanding uploaded files.

### Input Types

- PDFs
- Excel Files
- CSV Files
- Word Documents

## Extracted Information

### Financial Data

Revenue Profit Expenses Assets Liabilities Cash Flow

### ESG Data

Carbon Emissions Energy Usage Water Consumption

### Legal Data

Clauses Obligations Penalties Regulations

### Compliance Data

Violations Policies Risk Controls

## Stage 2: Text Processing

Pipeline:

Raw Text ↓ Cleaning ↓ Chunking ↓ Metadata Extraction ↓ Embedding

## Stage 3: Vector Indexing

All document chunks are stored in:

**pgvector** or

**Pinecone** Metadata includes:

{ "page": 56, "document": "Annual Report", "section": "Revenue Analysis" }

# Multi-Agent Architecture

The core innovation of the platform.

## Router Agent

**Purpose** Master decision-making agent. Receives user requests such as:

### Analyze ESG compliance risks.

Determines:

Need Retrieval Need ESG Analysis Need Audit Need Verification

### Routes tasks to specialized agents.

**Models**

- GPT-5
- Claude
- Other high-reasoning models

## Extraction Agent

**Purpose** Extract structured information from documents. Models:

- Qwen
- Llama
- Ollama-hosted models

Produces:

{ "company": "ABC Corp", "revenue": "$2.1B", "emissions": "12%" }

Responsibilities:

- Entity Extraction
- Financial Extraction
- Table Understanding
- Metadata Creation

## Search Agent

**Purpose** Advanced Retrieval-Augmented Generation. Pipeline:

Chunk Retrieval ↓ Embedding Search ↓ Hybrid Search ↓ Reranking ↓ Context Building

Technologies:

- pgvector
- Pinecone
- FlashRank
- Cohere Rerank

## Audit Agent

**Purpose** Cross-verifies extracted information. Example: Extraction Agent:

### Revenue = $2.1B

### Audit Agent checks:

### Verifies consistency.

## ESG Analysis Agent

Specialized sustainability reviewer. Analyzes:

- Carbon emissions
- Climate commitments
- Net-zero targets
- Sustainability disclosures
- ESG risks
  Produces:

ESG Score Risk Score Compliance Rating

## Verification Agent

Validates evidence quality. Responsibilities:

- Evidence matching
- Confidence scoring
- Citation verification
- Source validation
  Output:

Claim Supported Claim Weak Claim Unsupported

## Critic Agent

The most important component. Purpose:

- Detect hallucinations
- Challenge assumptions
- Verify calculations
- Validate evidence
  Example: Claim:

### Emissions reduced 25%

Evidence:

Source indicates 12%

Result:

### Claim Rejected

### This dramatically increases trustworthiness.

# LangGraph Workflow

LangGraph provides stateful orchestration. Workflow:

Router ↓ Extraction ↓ Search ↓ Audit ↓ Verification ↓ Critic ↓ Final Report

Benefits:

- Shared State
- Agent Memory
- Retry Logic
- Conditional Routing
- Human Approval Nodes

# Hybrid RAG System

A production-grade retrieval system.

## Chunking

Documents are split into:

- Semantic Chunks
- Financial Sections
- Legal Sections
- ESG Sections

## Embeddings

Generated using modern embedding models. Stored in:

pgvector or Pinecone

## Hybrid Search

Combines:

### Dense Retrieval

Captures semantic meaning.

### Sparse Retrieval

Captures exact keyword matches. Results are merged.

## Reranking

Top results pass through:

- FlashRank
- Cohere Rerank
  Ensuring the most relevant evidence is selected.

# Agent Monitoring Dashboard

Provides complete transparency. Displays:

Agent Status Execution Time Cost Retries Tokens Used Confidence Score

Example:

Router Agent Completed Extraction Agent Completed Audit Agent Running Critic Agent Waiting

**Source Verification Interface**

Every claim must be traceable. Example:

Claim: Revenue Increased 18% Evidence: Annual Report Page: 56 Confidence: 98%

Users can click evidence and jump directly to the supporting source.

# Report Generation System

Produces executive-ready reports. Sections include:

## Executive Summary

High-level findings.

## Financial Analysis

Revenue trends. Profitability. Cash flow observations.

## Compliance Findings

Policy violations. Regulatory risks. Audit observations.

## ESG Assessment

Carbon emissions. Sustainability goals. Climate compliance.

## Risk Analysis

Financial risks.

Governance risks. Operational risks.

## Recommendations

Actionable next steps.

## Evidence References

Every conclusion linked to supporting sources.

# Database Design

## PostgreSQL Tables

**users** Stores user accounts.

**organizations** Stores company workspaces.

**documents** Stores uploaded documents.

**jobs** Stores processing jobs.

**reports** Stores generated reports.

**agent\_runs** Stores execution history.

**audit\_logs** Stores verification actions.

# Vector Database Schema

## document\_chunks

Stores chunked content.

## embeddings

Stores vector embeddings.

## metadata

Stores:

Page Number Section Document Type Timestamp

# Human-in-the-Loop Review

Enterprise-grade verification layer. Allows auditors to:

- Approve findings
- Reject findings
- Edit reports
- Request re-analysis
  This creates a collaborative AI workflow rather than a fully autonomous black-box system.

# Key Engineering Skills Demonstrated

This project showcases advanced industry-level capabilities:

### AI & Agent Systems

- Multi-Agent AI
- LangGraph
- Agent Routing
- Agent Memory
- Critic Agents
- Verification Agents

### Retrieval Systems

- Hybrid RAG
- Vector Search
- Reranking
- Embedding Pipelines

### Backend Engineering

- FastAPI
- NestJS
- Redis
- BullMQ
- Async Processing

### Database Engineering

- PostgreSQL
- pgvector
- Pinecone
- Supabase

### Frontend Engineering

- Next.js
- React
- TypeScript
- Data Visualization
- Real-Time Dashboards

### Enterprise Features

- RBAC

- Multi-Tenancy

- Audit Trails

- Monitoring

- Human-in-the-Loop Validation


# Final Outcome

The Multi-Agent Corporate Governance & Document Analytics Engine is not a simple document chatbot. It is a fully featured enterprise AI platform that combines autonomous agents, advanced retrieval systems, governance analytics, audit verification, ESG intelligence, and executive reporting into a production-grade solution. The platform demonstrates how modern AI systems can move beyond basic question answering and evolve into trustworthy, auditable, and explainable decision-support systems suitable for financial institutions, consulting firms, regulators, auditors, legal teams, and corporate governance professionals.
    """

    # chunks = text_chunking(markdown_document)
    # # text_to_embed = [chunk.page_content for chunk in chunks]
    # embeddings = generate_embeddings_for_chunks(chunks)
    # print(text_to_embed)