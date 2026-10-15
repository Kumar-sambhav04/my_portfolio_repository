'use strict';

const menuToggle = document.querySelector('.menu-toggle');
const nav = document.querySelector('.main-nav');
const setMenu = (open) => {
  menuToggle.setAttribute('aria-expanded', String(open));
  menuToggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
  nav.classList.toggle('open', open);
};
menuToggle.addEventListener('click', () => setMenu(menuToggle.getAttribute('aria-expanded') !== 'true'));
nav.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => setMenu(false)));
document.addEventListener('keydown', (event) => { if (event.key === 'Escape') setMenu(false); });
document.addEventListener('click', (event) => {
  if (!nav.contains(event.target) && !menuToggle.contains(event.target)) setMenu(false);
});
window.addEventListener('resize', () => { if (window.innerWidth > 700) setMenu(false); });

const descriptions = {
  documents: 'Retrieve policy evidence with dense + BM25 search and return a grounded answer with citations.',
  sql: 'Query operational data through role-specific PostgreSQL connections and validate the SQL before execution.',
  hybrid: 'Combine document evidence and SQL data, with bounded corrective retrieval.'
};
const diagram = document.querySelector('.architecture-card');
document.querySelectorAll('.route-switch button').forEach((button) => {
  button.addEventListener('click', () => {
    const route = button.dataset.route;
    diagram.dataset.route = route;
    document.querySelectorAll('.route-switch button').forEach((item) => item.setAttribute('aria-pressed', String(item === button)));
    document.getElementById('route-description').textContent = descriptions[route];
  });
});

const studies = {
  rag: {
    eyebrow: '01 / FLAGSHIP PROJECT · RGD TECH',
    title: 'Corrective Hybrid RAG',
    subtitle: 'Python · LangGraph · Gemini · Pinecone · PostgreSQL · Streamlit',
    overview: `<h3>The business problem</h3><p>A support question can need both policy evidence and an operational fact. A document-only assistant cannot reliably answer an order-specific question, while a SQL-only system cannot explain a warranty policy.</p><p>I built RGD Tech as an independent portfolio application for a fictional business, bringing those two sources into one workflow.</p><h3>What the application does</h3><ul><li>Routes questions to document retrieval, Text-to-SQL, or a combination of both.</li><li>Combines evidence to generate an answer with source citations.</li><li>Separates support and admin access before forming the model’s context.</li></ul><p class="case-scope">Working portfolio application using policy PDFs and seeded business tables.</p>`,
    architecture: `<h3>One question, three routes</h3><ol><li><strong>Resolve the conversation:</strong> use conversation context to interpret follow-up questions.</li><li><strong>Choose the source:</strong> route to RAG, SQL, or a hybrid path using LangGraph.</li><li><strong>Retrieve the evidence:</strong> search Pinecone indexes for policy chunks and query PostgreSQL for structured records.</li><li><strong>Apply access controls:</strong> filter evidence according to the support or admin role before context assembly.</li><li><strong>Check and answer:</strong> evaluate available evidence and produce a cited response. Hybrid queries can make up to two corrective retrieval attempts.</li></ol><h3>Deliberate boundaries</h3><p>Corrective retries are bounded and apply to the hybrid path. RAG-only and SQL-only paths do not run that corrective loop.</p>`,
    implementation: `<h3>Retrieval and orchestration</h3><ul><li><strong>PDF ingestion:</strong> page-aware extraction and section-aware chunking preserve traceable source metadata.</li><li><strong>Hybrid search:</strong> 105 PDF chunks are represented in both dense and BM25 Pinecone indexes with shared chunk identifiers.</li><li><strong>Ranking:</strong> reciprocal rank fusion combines retrieval results; a CrossEncoder reranks candidates.</li><li><strong>Structured data:</strong> PostgreSQL on AWS RDS supports Text-to-SQL, validation, and query execution.</li><li><strong>Application state:</strong> conversation checkpoints support follow-up interaction in a Streamlit interface.</li><li><strong>Database separation:</strong> runtime connections use role-specific credentials, separate from schema setup credentials.</li></ul><div class="case-stack"><span>LangGraph</span><span>Gemini</span><span>Pinecone</span><span>BM25</span><span>PostgreSQL</span><span>AWS RDS</span><span>Streamlit</span></div>`
  },
  research: {
    eyebrow: '02 / AI AGENT WORKFLOW',
    title: 'Blog Research & Writing Agent',
    subtitle: 'Python · LangGraph · Gemini · Conditional web research',
    overview: `<h3>A workflow around the writing task</h3><p>This independent LangGraph project turns a topic into a planned response. The agent creates an outline, decides whether it needs additional research, gathers context when needed, and then generates the draft.</p><h3>What it demonstrates</h3><ul><li>Breaking a task into explicit planning, research, and writing stages.</li><li>Using conditional routing to decide whether web research is necessary.</li><li>Passing the topic, outline, and gathered context through shared graph state.</li><li>Generating a response that follows the plan.</li></ul><p class="case-scope">An independently built blog-generation workflow using LangGraph and Gemini.</p>`,
    architecture: `<h3>From input to draft</h3><ol><li><strong>Accept the topic:</strong> initialize the graph state with the title or writing request.</li><li><strong>Create the plan:</strong> generate an outline that guides the content.</li><li><strong>Decide on research:</strong> choose whether additional website context is needed.</li><li><strong>Gather context when needed:</strong> perform research and compile the relevant material.</li><li><strong>Write the response:</strong> generate the draft using the outline and available context.</li></ol><p>Conditional research makes this a multi-step agent workflow with an explicit decision point.</p>`,
    implementation: `<h3>Implementation focus</h3><ul><li>Orchestrated the workflow with LangGraph and Gemini.</li><li>Used shared state to carry the title, outline, and generated content between stages.</li><li>Separated planning from content generation.</li><li>Added the decision to research before assembling context for the draft.</li></ul><div class="case-stack"><span>Python</span><span>LangGraph</span><span>Gemini</span><span>Conditional routing</span><span>Shared state</span></div>`
  },
  chatbot: {
    eyebrow: '03 / TOOL USING ASSISTANT',
    title: 'LangGraph Tool Using Chatbot',
    subtitle: 'LangGraph · Gemini · Streamlit · LangSmith',
    overview: `<h3>Moving beyond a text-only reply</h3><p>This independent project explores how a conversational assistant can choose a useful tool, incorporate its result, and stream a response back to the user.</p><h3>What I built</h3><ul><li>A Gemini-based conversation workflow orchestrated with LangGraph.</li><li>Search and calculator tools that the assistant can call when needed.</li><li>A Streamlit interface with streamed responses.</li><li>Execution tracing through LangSmith.</li></ul>`,
    architecture: `<h3>The interaction loop</h3><ol><li>The user submits a message in Streamlit.</li><li>The Gemini model evaluates the request within the LangGraph workflow.</li><li>When needed, a ToolNode executes search or calculator calls.</li><li>Tool results return to the conversation so the assistant can form a response.</li><li>The response streams back to the interface while LangSmith captures the execution trace.</li></ol><p>The focus is a working tool-use loop with an interface that makes the interaction usable.</p>`,
    implementation: `<h3>Implementation focus</h3><ul><li>Routing model tool calls through a LangGraph ToolNode.</li><li>Maintaining the message sequence across model and tool responses.</li><li>Streaming response content into Streamlit.</li><li>Using LangSmith traces to inspect tool selection and workflow execution.</li></ul><div class="case-stack"><span>Python</span><span>LangGraph</span><span>Gemini</span><span>ToolNode</span><span>Streamlit</span><span>LangSmith</span></div>`
  },
  spotify: {
    eyebrow: '04 / MACHINE LEARNING',
    title: 'Spotify Song Recommender',
    subtitle: 'Python · scikit-learn · TF-IDF · FAISS · Streamlit',
    overview: `<h3>Finding related songs through their content</h3><p>A content-based recommendation project using roughly 114,000 song records. The user selects a song and receives five related recommendations through a Streamlit interface.</p><h3>What I built</h3><ul><li>Text-based track representations using TF-IDF.</li><li>Normalized vectors and a FAISS similarity index.</li><li>A retrieval flow that returns five recommendations.</li><li>A Streamlit interface for choosing a track and exploring the results.</li></ul>`,
    architecture: `<h3>From track metadata to recommendations</h3><ol><li>Prepare song metadata and construct the text features used for comparison.</li><li>Convert those text features to TF-IDF vectors.</li><li>Normalize the vector representations for similarity search.</li><li>Index the vectors using FAISS.</li><li>Look up the selected track’s representation and retrieve five related songs for the interface.</li></ol><p>Recommendations are generated from track content similarity.</p>`,
    implementation: `<h3>The second iteration</h3><p>The recommender moved from a KNN-based first version to a TF-IDF and FAISS implementation.</p><ul><li>Used a normalized FAISS IndexFlatIP representation for similarity search.</li><li>Saved model artifacts and reconstructed the index at runtime.</li><li>Kept large index artifacts out of the Git repository.</li><li>Connected retrieval results to a Streamlit application.</li></ul><div class="case-stack"><span>Python</span><span>TF-IDF</span><span>scikit-learn</span><span>FAISS</span><span>Streamlit</span></div>`
  }
};

const dialog = document.getElementById('case-dialog');
const tabs = [...document.querySelectorAll('.case-tabs [role="tab"]')];
let currentStudy = 'rag';
let previousFocus = null;
const selectTab = (name, focus = false) => {
  const selected = tabs.find((tab) => tab.dataset.tab === name);
  tabs.forEach((tab) => {
    tab.setAttribute('aria-selected', String(tab === selected));
    tab.tabIndex = tab === selected ? 0 : -1;
  });
  const panel = document.getElementById('case-panel');
  panel.innerHTML = studies[currentStudy][name];
  panel.setAttribute('aria-labelledby', selected.id);
  if (focus) selected.focus();
};
document.querySelectorAll('[data-case]').forEach((button) => {
  button.addEventListener('click', () => {
    currentStudy = button.dataset.case;
    previousFocus = button;
    const study = studies[currentStudy];
    document.getElementById('case-eyebrow').textContent = study.eyebrow;
    document.getElementById('case-title').textContent = study.title;
    document.getElementById('case-subtitle').textContent = study.subtitle;
    selectTab('overview');
    dialog.showModal();
    document.body.classList.add('dialog-open');
    dialog.scrollTop = 0;
  });
});
tabs.forEach((tab, index) => {
  tab.addEventListener('click', () => selectTab(tab.dataset.tab));
  tab.addEventListener('keydown', (event) => {
    let next = null;
    if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
    if (event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = tabs.length - 1;
    if (next !== null) { event.preventDefault(); selectTab(tabs[next].dataset.tab, true); }
  });
});
document.querySelector('.dialog-close').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', (event) => {
  const bounds = dialog.getBoundingClientRect();
  if (event.target === dialog && (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom)) dialog.close();
});
dialog.addEventListener('close', () => {
  document.body.classList.remove('dialog-open');
  if (previousFocus) previousFocus.focus();
});

document.querySelector('.copy-email').addEventListener('click', async () => {
  const status = document.querySelector('.copy-status');
  try {
    if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
    await navigator.clipboard.writeText('sambhavdubey214@gmail.com');
    status.textContent = 'Email address copied.';
  } catch {
    status.textContent = 'Select the email address to copy it, or click it to open your email app.';
  }
});

if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        nav.querySelectorAll('a[href^="#"]').forEach((link) => {
          const active = link.getAttribute('href') === '#' + entry.target.id;
          link.classList.toggle('active', active);
          if (active) link.setAttribute('aria-current', 'location');
          else link.removeAttribute('aria-current');
        });
      }
    });
  }, { rootMargin: '-15% 0px -65% 0px', threshold: 0 });
  document.querySelectorAll('main section[id]').forEach((section) => observer.observe(section));
}
