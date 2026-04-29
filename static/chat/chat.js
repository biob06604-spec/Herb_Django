const chatBox = document.getElementById("chat-box");
const input = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");
const clearBtn = document.getElementById("clear-btn");
const promptCards = document.querySelectorAll(".prompt-card");
const emptyState = document.getElementById("empty-state");
const recentList = document.getElementById("recent-list");

function createEmptyState() {
    const wrapper = document.createElement("div");
    wrapper.className = "empty-state";
    wrapper.id = "empty-state";
    wrapper.innerHTML = `
        <div class="empty-state-inner">
            <h3>What can I help you with?</h3>
            <p>
                你可以直接输入基因名如 <strong>AHR</strong>，
                或使用推荐问题，例如“查询 ESR1 相关药物”“查询大麻成分”。
            </p>
        </div>
    `;
    return wrapper;
}

function removeEmptyState() {
    const node = document.getElementById("empty-state");
    if (node) {
        node.remove();
    }
}

function appendRecentQuestion(text) {
    if (!recentList || !text) return;

    const item = document.createElement("div");
    item.className = "prompt-card recent-item";
    item.setAttribute("data-prompt", text);
    item.style.padding = "12px";
    item.innerHTML = `<p style="margin: 0; color: #374151;">${text}</p>`;

    item.addEventListener("click", () => {
        input.value = text;
        input.focus();
    });

    recentList.prepend(item);

    while (recentList.children.length > 5) {
        recentList.removeChild(recentList.lastElementChild);
    }
}

// 修改后的 appendMessage，增加返回 DOM 节点的功能
function appendMessage(role, text, toolUsed = null, isLoading = false) {
    removeEmptyState();

    const row = document.createElement("div");
    row.className = `msg-row ${role === "user" ? "user-row" : "assistant-row"}`;

    const div = document.createElement("div");
    div.className = `msg ${role}`;
    // 如果是加载中，给个特殊的 class 方便写 CSS
    if (isLoading) div.classList.add("loading-msg");

    const roleDiv = document.createElement("div");
    roleDiv.className = "msg-role";
    roleDiv.textContent = role === "user" ? "你" : "助手";

    const pre = document.createElement("pre");
    pre.textContent = text;

    div.appendChild(roleDiv);
    div.appendChild(pre);

    // 如果有工具，显示工具标签
    if (toolUsed) {
        const badge = document.createElement("div");
        badge.className = "tool-badge";
        badge.textContent = `调用工具：${toolUsed}`;
        div.appendChild(badge);
    }

    row.appendChild(div);
    chatBox.appendChild(row);
    chatBox.scrollTop = chatBox.scrollHeight;

    return div; // 【关键】返回这个消息框的引用，方便后续修改内容
}

async function sendMessage() {
    const message = input.value.trim();
    if (!message) return;

    appendMessage("user", message);
    appendRecentQuestion(message);
    input.value = "";

    const assistantMsgDiv = appendMessage("assistant", "正在思考并查询数据库...", null, true);
    const preTag = assistantMsgDiv.querySelector("pre");

    try {
        const response = await fetch("/chat/api/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });

        const data = await response.json();

        // --- 新增：移除加载状态并更新内容 ---
        assistantMsgDiv.classList.remove("loading-msg");
        
        if (data.error) {
            preTag.textContent = `错误：${data.error}`;
            return;
        }

        // 更新最终回答
        preTag.textContent = data.answer || "未返回内容";

        // 如果后端返回了使用的工具，动态加上工具标签
        if (data.tool_used) {
            const badge = document.createElement("div");
            badge.className = "tool-badge";
            badge.textContent = `已使用工具：${data.tool_used}`;
            assistantMsgDiv.appendChild(badge);
        }

    } catch (error) {
        assistantMsgDiv.classList.remove("loading-msg");
        preTag.textContent = `请求失败：${error.message}`;
    }
}

function clearChat() {
    chatBox.innerHTML = "";
    chatBox.appendChild(createEmptyState());
}

sendBtn.addEventListener("click", sendMessage);

if (clearBtn) {
    clearBtn.addEventListener("click", clearChat);
}

input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        sendMessage();
    }
});

promptCards.forEach(card => {
    card.addEventListener("click", () => {
        const prompt = card.getAttribute("data-prompt");
        input.value = prompt;
        input.focus();
    });
});