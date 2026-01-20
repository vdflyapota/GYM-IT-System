document.addEventListener("DOMContentLoaded", () => {
  const socket = io();
  const board = document.getElementById("board");

  const render = (data) => {
    board.innerHTML = "";
    data.leaderboard.forEach((row) => {
      const div = document.createElement("div");
      div.className = "row";
      div.innerHTML = `<span>${row.name}</span><span>${row.points}</span>`;
      board.appendChild(div);
    });
  };

  socket.on("connect", () => {
    console.log("Connected for realtime updates");
  });

  socket.on("leaderboard_update", (data) => {
    render(data);
  });
});
