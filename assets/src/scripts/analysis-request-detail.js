function generatePDF() {
  const downloadBtn = document.getElementById("downloadBtn");

  const report = document.getElementById("reportContainer");
  const watermark = report.querySelector("#watermark");
  const reportStyles = report.querySelector("#report");

  const dialog = document.getElementById("downloadModal");
  const confirmBtn = dialog.querySelector(`[value="confirm"]`);
  const cancelBtn = dialog.querySelector(`[value="cancel"]`);
  const generatingBtn = dialog.querySelector(`[value="generating"]`);

  const options = {
    margin: 15,
    filename: `${downloadBtn.dataset.title} - Report.pdf`,
    image: { type: "jpeg", quality: 0.75 },
    jsPDF: { unit: "mm", format: "a4", orientation: "portrait" },
    html2canvas: {
      scale: 2,
    },
    pagebreak: { mode: "avoid-all" },
  };

  let pdf;

  downloadBtn.addEventListener("click", async () => {
    dialog.showModal();

    // Load the JS on button click
    const html2pdf = await import("html2pdf.js");

    // Reset the font size for printing
    reportStyles.classList.add(`print-font`);

    // Remove elements not required
    report
      .querySelectorAll("svg")
      .forEach((element) => element.classList.add("!hidden"));
    report.querySelector(".toc").classList.add("!hidden");

    // Repeat the watermark 300 times on the container
    const singleInner = watermark.innerHTML;
    watermark.classList.remove("hidden");
    watermark.innerHTML = watermark.innerHTML.repeat(300);

    // Generate and download the PDF
    pdf = html2pdf
      .default()
      .set(options)
      .from(reportStyles)
      .toContainer()
      .toPdf();
    await pdf;

    // 0 timeout to remove watermark after the event loop has finished
    setTimeout(() => {
      watermark.classList.add("hidden");
      watermark.innerHTML = singleInner;
      reportStyles.classList.remove(`print-font`);
      report
        .querySelectorAll("svg")
        .forEach((element) => element.classList.remove("!hidden"));
      report.querySelector(".toc").classList.remove("!hidden");
    }, 0);

    // Show download button
    confirmBtn.classList.remove("hidden");
    generatingBtn.remove();
  });

  confirmBtn.addEventListener("click", () => {
    // When confirm is clicked, save the PDF
    pdf.save();

    // Wait 1s then close the dialog
    setTimeout(() => dialog.close(), 1000);
  });

  cancelBtn.addEventListener("click", () => {
    dialog.close();
  });
}

function formatNumbers() {
  const numbers = document.querySelectorAll(`[data-format-number="true"]`);
  numbers?.forEach(
    // eslint-disable-next-line no-return-assign
    (number) =>
      // eslint-disable-next-line no-param-reassign
      (number.textContent = parseFloat(number.textContent).toLocaleString(
        "en-GB"
      ))
  );
}

function addMenuButton() {
  if (document.querySelector("#tableOfContents")) {
    const menuBtn = document.createElement("a");
    menuBtn.id = "menuBtn";
    menuBtn.textContent = "Back to table of content";
    menuBtn.href = "#tableOfContents";
    document.querySelector("main").appendChild(menuBtn);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  generatePDF();
  formatNumbers();
  addMenuButton();
});
