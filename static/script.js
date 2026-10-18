const $ = (id) => document.getElementById(id);
let stream = null;
let selectedBlob = null;
let lastSpeech = "";

function showResult(text) {
  $("resultContent").textContent = text;
  $("speak").disabled = !text;
  lastSpeech = text;
}
function setStatus(text) { $("resultStatus").textContent = text; }
function showPreview(src) {
  $("placeholder").hidden = true;
  $("video").hidden = true;
  $("preview").hidden = false;
  $("preview").src = src;
}
async function stopCamera() {
  if (stream) stream.getTracks().forEach(t => t.stop());
  stream = null;
}
$("startCamera").addEventListener("click", async () => {
  try {
    await stopCamera();
    stream = await navigator.mediaDevices.getUserMedia({video:{facingMode:"environment"},audio:false});
    $("preview").hidden = true; $("placeholder").hidden = true;
    $("video").hidden = false; $("video").srcObject = stream;
    $("capture").disabled = false;
    $("startCamera").textContent = "Camera active";
  } catch (e) {
    alert("Camera could not start. Allow camera permission or use Upload image. Camera access generally requires localhost or HTTPS.");
  }
});
$("capture").addEventListener("click", () => {
  const video = $("video");
  if (!stream || !video.videoWidth) return;
  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth; canvas.height = video.videoHeight;
  canvas.getContext("2d").drawImage(video,0,0);
  canvas.toBlob(blob => {
    selectedBlob = blob;
    showPreview(URL.createObjectURL(blob));
    $("capture").disabled = true;
    $("startCamera").textContent = "Restart camera";
    stopCamera();
  }, "image/jpeg", .9);
});
$("imageFile").addEventListener("change", e => {
  const file = e.target.files[0];
  if (!file) return;
  if (file.size > 8*1024*1024) { alert("Please choose an image under 8 MB."); e.target.value=""; return; }
  selectedBlob = file;
  showPreview(URL.createObjectURL(file));
  $("capture").disabled = true;
  stopCamera();
});
$("analyze").addEventListener("click", async () => {
  if (!selectedBlob) { alert("Start the camera and capture an image, or upload an image first."); return; }
  const form = new FormData();
  form.append("image", selectedBlob, "scan.jpg");
  form.append("question", $("scanQuestion").value.trim());
  $("analyze").disabled = true; $("analyze").textContent = "Analyzing…"; setStatus("WORKING");
  showResult("Analyzing your image. This may take a moment…");
  try {
    const res = await fetch("/api/scan",{method:"POST",body:form});
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Scan failed.");
    let output = data.result || "No result was returned.";
    if (data.extracted_text) output += "\n\n--- TEXT DETECTED BY OCR ---\n" + data.extracted_text;
    showResult(output); setStatus("COMPLETE"); loadHistory();
  } catch(e) { showResult(e.message); setStatus("ERROR"); }
  finally { $("analyze").disabled=false; $("analyze").textContent="✦ Analyze with AI"; }
});
$("askForm").addEventListener("submit", async e => {
  e.preventDefault();
  const question = $("question").value.trim();
  if (!question) return;
  $("askResult").textContent = "Thinking…";
  const button = e.submitter; button.disabled = true;
  try {
    const res = await fetch("/api/ask",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({question})});
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Could not answer.");
    $("askResult").textContent = data.answer; loadHistory();
  } catch(err) { $("askResult").textContent = err.message; }
  finally { button.disabled=false; }
});
$("speak").addEventListener("click", () => {
  if (!lastSpeech || !("speechSynthesis" in window)) { alert("Text-to-speech is not supported in this browser."); return; }
  speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(lastSpeech);
  utterance.rate = 1; speechSynthesis.speak(utterance); $("stopSpeak").disabled=false;
});
$("stopSpeak").addEventListener("click", () => { speechSynthesis.cancel(); $("stopSpeak").disabled=true; });
$("refreshHistory").addEventListener("click", loadHistory);
async function loadHistory() {
  try {
    const res = await fetch("/api/history"); const rows = await res.json();
    const host = $("historyList"); host.innerHTML = "";
    if (!rows.length) { host.innerHTML = '<p class="muted">No scans yet. Your recent activity will appear here.</p>'; return; }
    rows.forEach(row => {
      const item = document.createElement("div"); item.className="history-item";
      const content = document.createElement("div");
      const title = document.createElement("strong"); title.textContent = `${row.kind} · ${row.created_at}`;
      const preview = document.createElement("p"); preview.textContent = row.result.length > 280 ? row.result.slice(0,280)+"…" : row.result;
      content.append(title,preview);
      const del = document.createElement("button"); del.className="button secondary delete"; del.textContent="Delete";
      del.addEventListener("click", async () => { await fetch(`/api/history/${row.id}`,{method:"DELETE"}); loadHistory(); });
      item.append(content,del); host.append(item);
    });
  } catch { $("historyList").innerHTML='<p class="muted">Could not load history.</p>'; }
}
window.addEventListener("beforeunload", stopCamera);
loadHistory();
