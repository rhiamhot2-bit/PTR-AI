const commands = [
  {
    name: "!design",
    purpose: "Jewelry concepts, collections, stone and metal ideas, product design briefs.",
    example: "!design Create a luxury emerald bridal ring concept."
  },
  {
    name: "!content",
    purpose: "Captions, ads, product descriptions, launch posts, and email copy.",
    example: "!content Write a Thai Facebook caption for an 18K diamond pendant."
  },
  {
    name: "!business",
    purpose: "Pricing ideas, customer service replies, sales scripts, and operation prompts.",
    example: "!business Help me price a custom 18K gold ring."
  },
  {
    name: "!veo",
    purpose: "Video generation prompts for jewelry showcases and campaigns.",
    example: "!veo Create an 8-second luxury jewelry video prompt in Thai."
  },
  {
    name: "!rhino",
    purpose: "Rhino, MatrixGold, 3D and CAD workflow help.",
    example: "!rhino Explain how to model a pave ring step by step."
  },
  {
    name: "!automation",
    purpose: "n8n workflow ideas, lead handling, order updates, and reports.",
    example: "!automation Create a Discord to Google Sheet order workflow."
  }
];

const commandList = document.getElementById("commandList");
const outputBox = document.getElementById("outputBox");
const webhookUrlInput = document.getElementById("webhookUrl");
const webhookStatus = document.getElementById("webhookStatus");

function renderCommands() {
  commandList.innerHTML = commands.map(command => `
    <article class="command-card">
      <h3>${command.name}</h3>
      <p>${command.purpose}</p>
      <code>${command.example}</code>
    </article>
  `).join("");
}

function loadWebhookUrl() {
  const savedUrl = localStorage.getItem("PTR_AI_WEBHOOK_URL") || "";
  webhookUrlInput.value = savedUrl;
  webhookStatus.textContent = savedUrl ? "Configured" : "Not connected";
}

function saveWebhookUrl() {
  const url = webhookUrlInput.value.trim();
  localStorage.setItem("PTR_AI_WEBHOOK_URL", url);
  webhookStatus.textContent = url ? "Configured" : "Not connected";
  outputBox.textContent = url
    ? "บันทึก n8n Webhook URL แล้วครับ"
    : "ยังไม่ได้ใส่ n8n Webhook URL";
}

function buildDesignerPayload() {
  return {
    command: "design",
    prompt: createDesignerPrompt(),
    business: "jewelry",
    source: "ptr_ai_dashboard",
    mode: "ai_designer",
    ai_designer: {
      jewelry_type: document.getElementById("jewelryType").value,
      style: document.getElementById("style").value.trim(),
      metal: document.getElementById("metal").value.trim(),
      main_stone: document.getElementById("mainStone").value.trim(),
      accent_stones: document.getElementById("accentStones").value.trim(),
      target_market: document.getElementById("targetMarket").value.trim(),
      budget_level: document.getElementById("budgetLevel").value,
      output_type: document.getElementById("outputType").value,
      notes: document.getElementById("notes").value.trim()
    }
  };
}

function createDesignerPrompt() {
  const jewelryType = document.getElementById("jewelryType").value;
  const style = document.getElementById("style").value.trim();
  const metal = document.getElementById("metal").value.trim();
  const mainStone = document.getElementById("mainStone").value.trim();
  const accentStones = document.getElementById("accentStones").value.trim();
  const targetMarket = document.getElementById("targetMarket").value.trim();
  const budgetLevel = document.getElementById("budgetLevel").value;
  const outputType = document.getElementById("outputType").value;
  const notes = document.getElementById("notes").value.trim();

  return [
    "You are PTR AI Designer, a jewelry design specialist.",
    `Create a ${outputType} for a ${jewelryType}.`,
    `Style: ${style}`,
    `Metal: ${metal}`,
    `Main stone: ${mainStone}`,
    `Accent stones: ${accentStones}`,
    `Target market: ${targetMarket}`,
    `Budget level: ${budgetLevel}`,
    `Notes: ${notes}`,
    "Return a clear jewelry concept with design details, CAD brief, stone map, and sales story when relevant."
  ].join("\n");
}

async function sendToN8n(event) {
  event.preventDefault();

  const webhookUrl = webhookUrlInput.value.trim() || localStorage.getItem("PTR_AI_WEBHOOK_URL") || "";
  const payload = buildDesignerPayload();

  if (!webhookUrl) {
    outputBox.textContent = "กรุณาใส่ n8n Webhook URL ก่อนส่งข้อมูลครับ";
    return;
  }

  outputBox.textContent = "กำลังส่งข้อมูลไปยัง n8n...";

  try {
    const response = await fetch(webhookUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const contentType = response.headers.get("content-type") || "";
    const data = contentType.includes("application/json")
      ? await response.json()
      : await response.text();

    outputBox.textContent = typeof data === "string"
      ? data
      : JSON.stringify(data, null, 2);
  } catch (error) {
    outputBox.textContent = `ส่งข้อมูลไม่สำเร็จ: ${error.message}`;
  }
}

function previewPayload() {
  const payload = buildDesignerPayload();
  outputBox.textContent = JSON.stringify(payload, null, 2);
}

renderCommands();
loadWebhookUrl();

document.getElementById("saveWebhook").addEventListener("click", saveWebhookUrl);
document.getElementById("previewPayload").addEventListener("click", previewPayload);
document.getElementById("designerForm").addEventListener("submit", sendToN8n);
