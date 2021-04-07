function deleteHour(hourId) {
  fetch("/delete-hour", {
    method: "POST",
    body: JSON.stringify({ hourId: hourId }),
  }).then((_res) => {
    window.location.href = "/hours";
  });
}