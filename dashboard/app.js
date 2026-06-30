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

const pageTitles = {
  home: "Home",
  designer: "AI Designer Pro",
  cad: "CAD Library",
  customers: "Customer Manager",
  orders: "Orders",
  discord: "Discord Control",
  n8n: "n8n Connection",
  analytics: "Analytics",
  settings: "Settings"
};

const commandList = document.getElementById("commandList");
const outputBox = document.getElementById("outputBox");
const webhookUrlInput = document.getElementById("webhookUrl");
const webhookStatus = document.getElementById("webhookStatus");
const topWebhookStatus = document.getElementById("topWebhookStatus");
const pageTitle = document.getElementById("pageTitle");

function renderCommands() {
  commandList.innerHTML = commands.map(command => `
    <article class="command-card">
      <h3>${command.name}</h3>
      <p>${command.purpose}</p>
      <code>${command.example}</code>
    </article>
  `).join("");
}

function switchPage(pageName) {
  document.querySelectorAll(".nav-item").forEach(button => {
    button.classList.toggle("active", button.dataset.page === pageName);
  });

  document.querySelectorAll(".page").forEach(page => {
    page.classList.remove("active");
  });

  const selectedPage = document.getElementById(`${pageName}Page`);
  if (selectedPage) {
    selectedPage.classList.add("active");
  }

  pageTitle.textContent = pageTitles[pageName] || "PTR AI";
}

function loadWebhookUrl() {
  const savedUrl = localStorage.getItem("PTR_AI_WEBHOOK_URL") || "";
  webhookUrlInput.value = savedUrl;
  updateWebhookStatus(savedUrl);
}

function updateWebhookStatus(url) {
  const status = url ? "Configured" : "Not connected";
  webhookStatus.textContent = status;
  topWebhookStatus.textContent = url ? "n8n: Configured" : "n8n: Not connected";
}

function saveWebhookUrl() {
  const url = webhookUrlInput.value.trim();
  localStorage.setItem("PTR_AI_WEBHOOK_URL", url);
  updateWebhookStatus(url);

  if (outputBox) {
    outputBox.textContent = url
      ? "บันทึก n8n Webhook URL แล้วครับ"
      : "ยังไม่ได้ใส่ n8n Webhook URL";
  }
}

function getDesignerData() {
  return {
    jewelry_type: document.getElementById("jewelryType").value,
    style: document.getElementById("style").value.trim(),
    metal: document.getElementById("metal").value.trim(),
    main_stone: document.getElementById("mainStone").value.trim(),
    accent_stones: document.getElementById("accentStones").value.trim(),
    target_market: document.getElementById("targetMarket").value.trim(),
    budget_level: document.getElementById("budgetLevel").value,
    output_type: document.getElementById("outputType").value,
    notes: document.getElementById("notes").value.trim()
  };
}

function buildDesignerPayload() {
  return {
    command: "design",
    prompt: createDesignerPrompt(),
    business: "jewelry",
    source: "ptr_ai_dashboard_v3",
    mode: "ai_designer_pro",
    ai_designer: getDesignerData()
  };
}

function createDesignerPrompt() {
  const data = getDesignerData();
  return [
    "You are PTR AI Designer Pro, a senior jewelry design specialist, CAD planner, gemstone stylist, and luxury brand storyteller.",
    `Create a ${data.output_type} for a ${data.jewelry_type}.`,
    `Style: ${data.style}`,
    `Metal: ${data.metal}`,
    `Main stone: ${data.main_stone}`,
    `Accent stones: ${data.accent_stones}`,
    `Target market: ${data.target_market}`,
    `Budget level: ${data.budget_level}`,
    `Notes: ${data.notes}`,
    "Return practical output for jewelry business use. Include CAD logic, gemstone placement, production notes, premium story, and sales angle when relevant."
  ].join("\n");
}

function setOutputType(outputType) {
  document.getElementById("outputType").value = outputType;
  document.querySelectorAll(".quick-output").forEach(button => {
    button.classList.toggle("active", button.dataset.output === outputType);
  });
}

function generateLocalDraft() {
  const data = getDesignerData();
  const title = `${data.style} ${data.jewelry_type} with ${data.main_stone}`;
  const outputType = data.output_type;

  const sections = {
    cad_brief: [
      `# CAD Brief: ${title}`,
      "",
      `Jewelry Type: ${data.jewelry_type}`,
      `Style Direction: ${data.style}`,
      `Metal: ${data.metal}`,
      `Main Stone: ${data.main_stone}`,
      `Accent Stones: ${data.accent_stones}`,
      "",
      "CAD Structure:",
      "- Create the main silhouette with balanced luxury proportions.",
      "- Build a secure center setting for the main stone.",
      "- Add accent stone positions with clean spacing and production-safe prongs.",
      "- Keep comfort-fit contact areas for daily wear.",
      "- Prepare model logic for Rhino / MatrixGold production workflow.",
      "",
      `Production Notes: ${data.notes}`
    ],
    stone_map: [
      `# Stone Map: ${title}`,
      "",
      `Center Stone: ${data.main_stone}`,
      `Accent Stones: ${data.accent_stones}`,
      "",
      "Suggested Mapping:",
      "- Center: 1 main stone as the visual hero.",
      "- Halo / border: small diamonds or accent stones following the main shape.",
      "- Side detail: balanced stone layout on left and right side.",
      "- Check stone spacing, prong clearance, and casting thickness.",
      "",
      "Next Step: Convert this into a numbered stone-setting map for CAD and setter communication."
    ],
    sales_story: [
      `# Sales Story: ${title}`,
      "",
      `This piece is designed for ${data.target_market}.`,
      `The ${data.main_stone} becomes the emotional center, supported by ${data.accent_stones}.`,
      `The ${data.metal} gives the piece a premium and warm luxury feeling.`,
      "",
      "Story Angle:",
      "- Royal elegance",
      "- Personal meaning",
      "- Premium craftsmanship",
      "- Timeless value",
      "",
      `Design Mood: ${data.notes}`
    ],
    sales_caption: [
      `# Sales Caption: ${title}`,
      "",
      `เครื่องประดับดีไซน์หรู สร้างจาก ${data.metal} พร้อม ${data.main_stone} เป็นหัวใจหลักของงาน`,
      `เสริมประกายด้วย ${data.accent_stones} เหมาะสำหรับ ${data.target_market}`,
      "",
      "งานนี้ออกแบบเพื่อคนที่ต้องการความงาม ความหมาย และคุณค่าที่อยู่ได้นาน",
      "",
      "#PTRAI #JewelryDesign #LuxuryJewelry #CADJewelry #เครื่องประดับหรู"
    ],
    veo_prompt: [
      `# Veo Prompt: ${title}`,
      "",
      "Create an 8-second luxury jewelry showcase video.",
      `Subject: ${data.jewelry_type} made of ${data.metal} with ${data.main_stone} and ${data.accent_stones}.`,
      `Style: ${data.style}.`,
      `Target feeling: premium, elegant, cinematic, royal, high jewelry.`,
      "Camera: slow macro rotation, soft studio lighting, gemstone sparkle, dark luxury background.",
      "No text, no logo, no watermark.",
      "Spoken language: Thai only if voice is used."
    ],
    rhino_steps: [
      `# Rhino Steps: ${title}`,
      "",
      "1. Set unit and reference scale for jewelry production.",
      "2. Create base curve or ring/pendant outline.",
      "3. Build main surface or solid body.",
      `4. Create center setting for ${data.main_stone}.`,
      `5. Add stone seats for ${data.accent_stones}.`,
      "6. Add prongs, bezels, or pavé details.",
      "7. Check thickness, spacing, casting safety, and stone clearance.",
      "8. Prepare render material and export production files."
    ],
    design_concept: [
      `# Design Concept: ${title}`,
      "",
      `A ${data.style} ${data.jewelry_type} designed for ${data.target_market}.`,
      `The design uses ${data.metal}, a ${data.main_stone}, and ${data.accent_stones}.`,
      "",
      "Key Design Details:",
      "- Strong center focus",
      "- Elegant symmetry",
      "- Premium gemstone balance",
      "- Production-aware construction",
      `- Notes: ${data.notes}`
    ]
  };

  outputBox.textContent = (sections[outputType] || sections.design_concept).join("\n");
}

async function sendToN8n(event) {
  event.preventDefault();

  const webhookUrl = webhookUrlInput.value.trim() || localStorage.getItem("PTR_AI_WEBHOOK_URL") || "";
  const payload = buildDesignerPayload();

  if (!webhookUrl) {
    outputBox.textContent = "กรุณาใส่ n8n Webhook URL ก่อนส่งข้อมูลครับ";
    switchPage("n8n");
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

async function copyOutput() {
  const text = outputBox.textContent || "";
  try {
    await navigator.clipboard.writeText(text);
    const oldText = outputBox.textContent;
    outputBox.textContent = "คัดลอก Output แล้วครับ\n\n" + oldText;
  } catch (error) {
    outputBox.textContent = "คัดลอกไม่สำเร็จ กรุณาลากเลือกข้อความแล้วคัดลอกเองครับ";
  }
}

renderCommands();
loadWebhookUrl();

document.querySelectorAll(".nav-item").forEach(button => {
  button.addEventListener("click", () => switchPage(button.dataset.page));
});

document.querySelectorAll(".module-card").forEach(card => {
  card.addEventListener("click", () => switchPage(card.dataset.jump));
});

document.querySelectorAll(".quick-output").forEach(button => {
  button.addEventListener("click", () => setOutputType(button.dataset.output));
});

document.getElementById("saveWebhook").addEventListener("click", saveWebhookUrl);
document.getElementById("previewPayload").addEventListener("click", previewPayload);
document.getElementById("generateLocal").addEventListener("click", generateLocalDraft);
document.getElementById("copyOutput").addEventListener("click", copyOutput);
document.getElementById("designerForm").addEventListener("submit", sendToN8n);
