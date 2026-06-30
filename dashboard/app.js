const commands = [
  { name: "!design", purpose: "Jewelry concepts, collections, stone and metal ideas, product design briefs.", example: "!design Create a luxury emerald bridal ring concept." },
  { name: "!content", purpose: "Captions, ads, product descriptions, launch posts, and email copy.", example: "!content Write a Thai Facebook caption for an 18K diamond pendant." },
  { name: "!business", purpose: "Pricing ideas, customer service replies, sales scripts, and operation prompts.", example: "!business Help me price a custom 18K gold ring." },
  { name: "!veo", purpose: "Video generation prompts for jewelry showcases and campaigns.", example: "!veo Create an 8-second luxury jewelry video prompt in Thai." },
  { name: "!rhino", purpose: "Rhino, MatrixGold, 3D and CAD workflow help.", example: "!rhino Explain how to model a pave ring step by step." },
  { name: "!automation", purpose: "n8n workflow ideas, lead handling, order updates, and reports.", example: "!automation Create a Discord to Google Sheet order workflow." }
];

const pageTitles = { home: "Home", designer: "AI Chat Designer", cad: "CAD Gallery", customers: "Customer CRM", orders: "Order Board", projects: "Saved Projects", discord: "Discord Control", n8n: "n8n Connection", analytics: "Analytics", settings: "Settings" };

const cadItems = [
  { type: "💍 Ring", title: "UAE Emerald Bridal Ring", tags: "ring emerald UAE 18K rose gold", status: "CAD Brief Ready" },
  { type: "📿 Necklace", title: "Royal Gem Necklace", tags: "necklace diamond emerald royal", status: "Render Idea" },
  { type: "💎 Pendant", title: "Sacred Geometry Pendant", tags: "pendant geometry spiritual diamond", status: "Concept" },
  { type: "👑 Brooch", title: "Arab Luxury Brooch", tags: "brooch ruby diamond middle east", status: "Stone Map Needed" },
  { type: "🧿 Bracelet", title: "Emerald Tennis Bracelet", tags: "bracelet emerald diamond", status: "Production Notes" },
  { type: "✨ Earrings", title: "Pear Diamond Earrings", tags: "earrings pear diamond bride", status: "CAD Steps" }
];

const customers = [
  { name: "Ahmed Al Noor", country: "UAE", budget: "350,000 THB", style: "Emerald bridal ring", status: "Waiting CAD" },
  { name: "คุณมณี", country: "Thailand", budget: "85,000 THB", style: "Pendant diamond", status: "Design Review" },
  { name: "Fatima", country: "Qatar", budget: "520,000 THB", style: "Full bridal set", status: "Quotation" }
];

const orders = {
  "Waiting": ["UAE Emerald Ring", "Qatar Bridal Set"],
  "CAD": ["Sacred Pendant"],
  "Casting": ["Diamond Earrings"],
  "Setting": ["Tennis Bracelet"],
  "Delivery": ["Royal Brooch"]
};

const commandList = document.getElementById("commandList");
const outputBox = document.getElementById("outputBox");
const webhookUrlInput = document.getElementById("webhookUrl");
const webhookStatus = document.getElementById("webhookStatus");
const topWebhookStatus = document.getElementById("topWebhookStatus");
const pageTitle = document.getElementById("pageTitle");

function renderCommands() {
  if (!commandList) return;
  commandList.innerHTML = commands.map(command => `<article class="command-card"><h3>${command.name}</h3><p>${command.purpose}</p><code>${command.example}</code></article>`).join("");
}

function switchPage(pageName) {
  document.querySelectorAll(".nav-item").forEach(button => button.classList.toggle("active", button.dataset.page === pageName));
  document.querySelectorAll(".page").forEach(page => page.classList.remove("active"));
  const selectedPage = document.getElementById(`${pageName}Page`);
  if (selectedPage) selectedPage.classList.add("active");
  pageTitle.textContent = pageTitles[pageName] || "PTR AI";
  if (pageName === "projects") renderSavedProjects();
}

function loadWebhookUrl() {
  const savedUrl = localStorage.getItem("PTR_AI_WEBHOOK_URL") || "";
  webhookUrlInput.value = savedUrl;
  updateWebhookStatus(savedUrl);
}

function updateWebhookStatus(url) {
  if (webhookStatus) webhookStatus.textContent = url ? "Configured" : "Not connected";
  if (topWebhookStatus) topWebhookStatus.textContent = url ? "n8n: Configured" : "n8n: Not connected";
}

function saveWebhookUrl() {
  const url = webhookUrlInput.value.trim();
  localStorage.setItem("PTR_AI_WEBHOOK_URL", url);
  updateWebhookStatus(url);
  if (outputBox) outputBox.textContent = url ? "บันทึก n8n Webhook URL แล้วครับ" : "ยังไม่ได้ใส่ n8n Webhook URL";
}

function getDesignerData() {
  const get = id => document.getElementById(id)?.value || "";
  return {
    jewelry_type: get("jewelryType"),
    style: get("style").trim(),
    metal: get("metal").trim(),
    main_stone: get("mainStone").trim(),
    accent_stones: get("accentStones").trim(),
    target_market: get("targetMarket").trim(),
    budget_level: get("budgetLevel"),
    output_type: get("outputType"),
    notes: get("notes").trim()
  };
}

function createDesignerPrompt() {
  const data = getDesignerData();
  return [`You are PTR AI Designer Pro.`, `Create a ${data.output_type} for ${data.jewelry_type}.`, `Style: ${data.style}`, `Metal: ${data.metal}`, `Main stone: ${data.main_stone}`, `Accent stones: ${data.accent_stones}`, `Target: ${data.target_market}`, `Notes: ${data.notes}`].join("\n");
}

function buildDesignerPayload() {
  return { command: "design", prompt: createDesignerPrompt(), business: "jewelry", source: "ptr_ai_dashboard_v5", mode: "ai_chat_designer", ai_designer: getDesignerData() };
}

function draftFromText(text, mode) {
  const title = text.split(",")[0] || "Luxury jewelry concept";
  const modeTitle = mode.replaceAll("_", " ").toUpperCase();
  return [`# ${modeTitle}: ${title}`, "", `Input: ${text}`, "", "Design Direction:", "- Luxury high-jewelry proportion", "- Clear center-stone focus", "- Balanced side details for production", "- Premium story for customer presentation", "", "CAD / Production Logic:", "- Build main silhouette first", "- Add center setting and gemstone seats", "- Check prong clearance, wall thickness, and comfort", "- Prepare render prompt and sales story"].join("\n");
}

function addChatMessage(role, text) {
  const chatBox = document.getElementById("chatBox");
  const div = document.createElement("div");
  div.className = `chat-message ${role}`;
  div.textContent = text;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function generateChat(mode) {
  const input = document.getElementById("chatPrompt").value.trim();
  if (!input) return;
  addChatMessage("user", input);
  const draft = draftFromText(input, mode);
  addChatMessage("bot", draft);
  outputBox.textContent = draft;
}

function setOutputType(outputType) {
  document.getElementById("outputType").value = outputType;
  document.querySelectorAll(".quick-output").forEach(button => button.classList.toggle("active", button.dataset.output === outputType));
}

function generateLocalDraft() {
  const data = getDesignerData();
  outputBox.textContent = draftFromText(`${data.style}, ${data.metal}, ${data.main_stone}, ${data.accent_stones}, ${data.target_market}`, data.output_type);
}

async function sendToN8n(event) {
  event.preventDefault();
  const webhookUrl = webhookUrlInput.value.trim() || localStorage.getItem("PTR_AI_WEBHOOK_URL") || "";
  if (!webhookUrl) { outputBox.textContent = "กรุณาใส่ n8n Webhook URL ก่อนส่งข้อมูลครับ"; switchPage("n8n"); return; }
  outputBox.textContent = "กำลังส่งข้อมูลไปยัง n8n...";
  try {
    const response = await fetch(webhookUrl, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(buildDesignerPayload()) });
    const contentType = response.headers.get("content-type") || "";
    const data = contentType.includes("application/json") ? await response.json() : await response.text();
    outputBox.textContent = typeof data === "string" ? data : JSON.stringify(data, null, 2);
  } catch (error) { outputBox.textContent = `ส่งข้อมูลไม่สำเร็จ: ${error.message}`; }
}

function previewPayload() { outputBox.textContent = JSON.stringify(buildDesignerPayload(), null, 2); }
async function copyOutput() { await navigator.clipboard.writeText(outputBox.textContent || ""); }

function renderCadGallery(filter = "") {
  const box = document.getElementById("cadGallery");
  if (!box) return;
  const keyword = filter.toLowerCase();
  box.innerHTML = cadItems.filter(item => `${item.title} ${item.tags}`.toLowerCase().includes(keyword)).map(item => `<article class="gallery-card"><div class="gallery-thumb">${item.type}</div><h3>${item.title}</h3><p>${item.tags}</p><span>${item.status}</span></article>`).join("");
}

function renderCustomers() {
  const box = document.getElementById("customerGrid");
  if (!box) return;
  box.innerHTML = customers.map(c => `<article class="customer-card"><h3>${c.name}</h3><p>${c.country}</p><strong>${c.budget}</strong><span>${c.style}</span><em>${c.status}</em></article>`).join("");
}

function renderOrders() {
  const box = document.getElementById("orderBoard");
  if (!box) return;
  box.innerHTML = Object.entries(orders).map(([stage, items]) => `<section class="kanban-column"><h3>${stage}</h3>${items.map(item => `<div class="order-card">${item}</div>`).join("")}</section>`).join("");
}

function getSavedProjects() {
  return JSON.parse(localStorage.getItem("PTR_AI_PROJECTS") || "[]");
}

function saveCurrentProject() {
  const prompt = document.getElementById("chatPrompt")?.value.trim() || "Untitled jewelry project";
  const output = outputBox?.textContent || "";
  const projects = getSavedProjects();
  const project = {
    id: `PTR-${Date.now()}`,
    title: prompt.slice(0, 60),
    prompt,
    output,
    status: "Waiting CAD",
    created_at: new Date().toLocaleString()
  };
  projects.unshift(project);
  localStorage.setItem("PTR_AI_PROJECTS", JSON.stringify(projects));
  renderSavedProjects();
  switchPage("projects");
}

function renderSavedProjects() {
  const box = document.getElementById("savedProjectsGrid");
  if (!box) return;
  const projects = getSavedProjects();
  if (projects.length === 0) {
    box.innerHTML = `<p class="muted">ยังไม่มี Project ที่บันทึก ลองไปที่ AI Chat Designer แล้วกด Save Project ครับ</p>`;
    return;
  }
  box.innerHTML = projects.map(project => `<article class="customer-card"><h3>${project.title}</h3><p>${project.created_at}</p><strong>${project.status}</strong><span>${project.prompt}</span><em>${project.id}</em></article>`).join("");
}

function installV5UI() {
  const nav = document.querySelector(".nav-menu");
  const ordersButton = document.querySelector('[data-page="orders"]');
  if (nav && !document.querySelector('[data-page="projects"]')) {
    const button = document.createElement("button");
    button.className = "nav-item";
    button.dataset.page = "projects";
    button.textContent = "🧠 Projects";
    nav.insertBefore(button, ordersButton?.nextSibling || nav.children[4]);
    button.addEventListener("click", () => switchPage("projects"));
  }

  const main = document.querySelector(".main-area");
  if (main && !document.getElementById("projectsPage")) {
    const section = document.createElement("section");
    section.className = "page";
    section.id = "projectsPage";
    section.innerHTML = `<section class="panel"><h2>Saved Projects</h2><p class="muted">V5 Foundation: บันทึกโปรเจกต์ลง Browser Local Storage ก่อน ต่อไปค่อยต่อ Database / Google Drive / n8n</p><div class="customer-grid" id="savedProjectsGrid"></div></section>`;
    main.appendChild(section);
  }

  const outputHeader = document.querySelector("#copyOutput")?.parentElement;
  if (outputHeader && !document.getElementById("saveProject")) {
    const button = document.createElement("button");
    button.type = "button";
    button.id = "saveProject";
    button.className = "secondary-button";
    button.textContent = "Save Project";
    outputHeader.appendChild(button);
    button.addEventListener("click", saveCurrentProject);
  }
}

renderCommands();
renderCadGallery();
renderCustomers();
renderOrders();
loadWebhookUrl();
installV5UI();
renderSavedProjects();

document.querySelectorAll(".nav-item").forEach(button => button.addEventListener("click", () => switchPage(button.dataset.page)));
document.querySelectorAll(".module-card").forEach(card => card.addEventListener("click", () => switchPage(card.dataset.jump)));
document.querySelectorAll(".quick-output").forEach(button => button.addEventListener("click", () => setOutputType(button.dataset.output)));
document.querySelectorAll(".chat-generate").forEach(button => button.addEventListener("click", () => generateChat(button.dataset.mode)));
document.getElementById("cadSearch")?.addEventListener("input", event => renderCadGallery(event.target.value));
document.getElementById("saveWebhook")?.addEventListener("click", saveWebhookUrl);
document.getElementById("previewPayload")?.addEventListener("click", previewPayload);
document.getElementById("generateLocal")?.addEventListener("click", generateLocalDraft);
document.getElementById("copyOutput")?.addEventListener("click", copyOutput);
document.getElementById("designerForm")?.addEventListener("submit", sendToN8n);
