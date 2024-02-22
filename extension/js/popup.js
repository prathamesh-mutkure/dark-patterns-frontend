window.onload = function () {
  chrome.tabs.query({ currentWindow: true, active: true }, function (tabs) {
    chrome.tabs.sendMessage(tabs[0].id, { message: "popup_open" });
  });

  document.getElementsByClassName("analyze-button")[0].onclick = function () {
    chrome.tabs.query({ currentWindow: true, active: true }, function (tabs) {
      chrome.tabs.sendMessage(tabs[0].id, { message: "analyze_site" });
    });
  };

  document.getElementsByClassName("link")[0].onclick = function () {
    chrome.tabs.create({
      url: document.getElementsByClassName("link")[0].getAttribute("href"),
    });
  };
};

chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  if (request.message === "update_current_count") {
    document.getElementsByClassName("number")[0].textContent = request.count;
  }
});

document.addEventListener("DOMContentLoaded", function () {
  var analyzeButton = document.getElementById("analyzeButton");
  var resultContainer = document.getElementById("resultContainer");

  analyzeButton.addEventListener("click", function () {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      var activeTab = tabs[0];
      chrome.tabs.sendMessage(activeTab.id, { action: "analyze" });
    });
  });

  chrome.runtime.onMessage.addListener(function (
    request,
    sender,
    sendResponse
  ) {
    if (request.action === "displayResults") {
      displayResults(request.data);
    }
  });

  function displayResults(data) {
    resultContainer.innerHTML = `
            <p><strong>Adherence Percentage:</strong> <span class="percentage">${data.adherencePercentage.toFixed(
              2
            )}%</span></p>
            <p><strong>Followed Rules:</strong> ${data.followedRules.join(
              ", "
            )}</p>
            <p><strong>Not Followed Rules:</strong> ${data.notFollowedRules.join(
              ", "
            )}</p>
        `;
  }
});
