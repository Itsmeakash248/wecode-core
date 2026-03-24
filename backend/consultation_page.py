"""
HTML renderer for the standalone WebRTC consultation page.
"""
from __future__ import annotations

import json
from html import escape
from string import Template
from typing import Any


PAGE_TEMPLATE = Template(
    """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>$page_title</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f3f7fb;
      --surface: #ffffff;
      --surface-soft: #edf3f9;
      --border: #d7e3ef;
      --text: #13263a;
      --muted: #5f7287;
      --accent: #0f766e;
      --accent-strong: #115e59;
      --warn: #b45309;
      --danger: #b91c1c;
      --shadow: 0 18px 45px rgba(18, 38, 58, 0.12);
      --radius: 20px;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      font-family: "Segoe UI", "Helvetica Neue", sans-serif;
      background:
        radial-gradient(circle at top left, rgba(15, 118, 110, 0.14), transparent 28%),
        linear-gradient(180deg, #f8fbfe 0%, var(--bg) 100%);
      color: var(--text);
      min-height: 100vh;
    }

    .shell {
      max-width: 1440px;
      margin: 0 auto;
      padding: 28px;
    }

    .header {
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
    }

    .header-copy h1 {
      margin: 0 0 8px;
      font-size: 2rem;
      line-height: 1.1;
    }

    .header-copy p {
      margin: 0;
      color: var(--muted);
      max-width: 760px;
    }

    .status-row {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
      justify-content: flex-end;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 10px 14px;
      border-radius: 999px;
      background: rgba(15, 118, 110, 0.1);
      color: var(--accent-strong);
      font-weight: 600;
    }

    .dot {
      width: 10px;
      height: 10px;
      border-radius: 999px;
      background: #16a34a;
      box-shadow: 0 0 0 5px rgba(22, 163, 74, 0.14);
    }

    .dot.offline {
      background: #dc2626;
      box-shadow: 0 0 0 5px rgba(220, 38, 38, 0.14);
    }

    .layout {
      display: grid;
      grid-template-columns: minmax(0, 2.2fr) minmax(320px, 0.9fr);
      gap: 20px;
    }

    .panel {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }

    .video-panel {
      padding: 18px;
      position: relative;
      overflow: hidden;
    }

    .video-stage {
      position: relative;
      border-radius: 18px;
      overflow: hidden;
      background:
        radial-gradient(circle at top right, rgba(15, 118, 110, 0.2), transparent 24%),
        linear-gradient(160deg, #16324a 0%, #091722 100%);
      min-height: 520px;
    }

    video {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      background: #0f172a;
    }

    #remote-video {
      min-height: 520px;
    }

    .placeholder {
      position: absolute;
      inset: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: rgba(255, 255, 255, 0.88);
      gap: 12px;
      text-align: center;
      padding: 28px;
    }

    .placeholder-title {
      font-size: 1.2rem;
      font-weight: 600;
    }

    .local-card {
      position: absolute;
      right: 18px;
      bottom: 18px;
      width: min(28vw, 240px);
      border-radius: 18px;
      overflow: hidden;
      border: 2px solid rgba(255, 255, 255, 0.45);
      box-shadow: 0 18px 30px rgba(0, 0, 0, 0.24);
      background: #0f172a;
    }

    .local-label {
      position: absolute;
      top: 10px;
      left: 10px;
      padding: 6px 10px;
      border-radius: 999px;
      background: rgba(15, 23, 42, 0.68);
      color: #fff;
      font-size: 0.78rem;
      letter-spacing: 0.02em;
      z-index: 2;
    }

    .controls {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 16px;
    }

    button,
    .link-button {
      border: 0;
      border-radius: 12px;
      padding: 12px 16px;
      font: inherit;
      font-weight: 600;
      cursor: pointer;
      transition: transform 0.14s ease, opacity 0.14s ease, background 0.14s ease;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }

    button:hover,
    .link-button:hover {
      transform: translateY(-1px);
    }

    button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
      transform: none;
    }

    .primary {
      background: var(--accent);
      color: #fff;
    }

    .secondary {
      background: var(--surface-soft);
      color: var(--text);
      border: 1px solid var(--border);
    }

    .danger {
      background: #fee2e2;
      color: var(--danger);
    }

    .meta-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 18px;
    }

    .meta-card {
      padding: 14px;
      border-radius: 16px;
      background: var(--surface-soft);
      border: 1px solid var(--border);
    }

    .meta-label {
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
      margin-bottom: 8px;
    }

    .meta-value {
      font-size: 1rem;
      font-weight: 600;
    }

    .side-panel {
      display: grid;
      grid-template-rows: auto minmax(0, 1fr);
      gap: 18px;
      padding: 18px;
      min-height: 720px;
    }

    .participants {
      padding: 16px;
      border-radius: 18px;
      border: 1px solid var(--border);
      background: var(--surface-soft);
    }

    .participants h2,
    .chat h2 {
      margin: 0 0 14px;
      font-size: 1rem;
    }

    .participant-list {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .participant-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      padding: 12px 14px;
      background: #fff;
      border: 1px solid var(--border);
      border-radius: 14px;
    }

    .participant-name {
      font-weight: 600;
    }

    .participant-role {
      color: var(--muted);
      font-size: 0.9rem;
    }

    .chat {
      display: grid;
      grid-template-rows: auto minmax(0, 1fr) auto;
      min-height: 0;
      padding: 16px;
      border-radius: 18px;
      border: 1px solid var(--border);
      background: var(--surface-soft);
    }

    .chat-feed {
      overflow: auto;
      min-height: 280px;
      max-height: 520px;
      padding-right: 6px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .chat-entry {
      padding: 12px 14px;
      border-radius: 16px;
      background: #fff;
      border: 1px solid var(--border);
    }

    .chat-entry.me {
      background: rgba(15, 118, 110, 0.08);
      border-color: rgba(15, 118, 110, 0.18);
    }

    .chat-meta {
      display: flex;
      gap: 8px;
      align-items: baseline;
      color: var(--muted);
      font-size: 0.82rem;
      margin-bottom: 6px;
    }

    .chat-author {
      font-weight: 700;
      color: var(--text);
    }

    .chat-text {
      white-space: pre-wrap;
      word-break: break-word;
      line-height: 1.45;
    }

    .chat-form {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 10px;
      margin-top: 14px;
    }

    textarea {
      resize: vertical;
      min-height: 82px;
      max-height: 180px;
      border-radius: 14px;
      border: 1px solid var(--border);
      padding: 12px 14px;
      font: inherit;
      color: var(--text);
      background: #fff;
    }

    .notice {
      margin-top: 18px;
      padding: 14px 16px;
      border-radius: 14px;
      background: #fff7ed;
      border: 1px solid #fed7aa;
      color: var(--warn);
      line-height: 1.45;
    }

    .error-banner {
      display: none;
      margin-bottom: 16px;
      padding: 14px 16px;
      border-radius: 14px;
      background: #fef2f2;
      border: 1px solid #fecaca;
      color: var(--danger);
      line-height: 1.45;
    }

    .error-banner.visible {
      display: block;
    }

    @media (max-width: 1080px) {
      .layout {
        grid-template-columns: 1fr;
      }

      .side-panel {
        min-height: 0;
      }
    }

    @media (max-width: 720px) {
      .shell {
        padding: 16px;
      }

      .header-copy h1 {
        font-size: 1.55rem;
      }

      .meta-grid {
        grid-template-columns: 1fr;
      }

      .video-stage,
      #remote-video {
        min-height: 320px;
      }

      .local-card {
        width: 38vw;
        min-width: 120px;
      }

      .chat-form {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="shell">
    <div class="header">
      <div class="header-copy">
        <h1>$room_heading</h1>
        <p>$room_subtitle</p>
      </div>
      <div class="status-row">
        <div class="badge"><span>Room</span><strong id="room-id">$room_id</strong></div>
        <div class="badge">
          <span id="status-dot" class="dot offline"></span>
          <span id="connection-status">Connecting</span>
        </div>
      </div>
    </div>

    <div id="error-banner" class="error-banner"></div>

    <div class="layout">
      <section class="panel video-panel">
        <div class="video-stage">
          <video id="remote-video" autoplay playsinline></video>
          <div id="remote-placeholder" class="placeholder">
            <div class="placeholder-title">Waiting for the other participant</div>
            <div>Open this consultation from both the patient and doctor dashboards to start the call.</div>
          </div>
          <div class="local-card">
            <div class="local-label">You</div>
            <video id="local-video" autoplay playsinline muted></video>
          </div>
        </div>

        <div class="controls">
          <button id="start-call" class="primary" type="button">Start camera and mic</button>
          <button id="toggle-mic" class="secondary" type="button" disabled>Mute mic</button>
          <button id="toggle-camera" class="secondary" type="button" disabled>Turn off camera</button>
          <button id="hangup" class="danger" type="button" disabled>Leave media session</button>
          <button id="reconnect" class="secondary" type="button">Reconnect signaling</button>
        </div>

        <div class="meta-grid">
          <div class="meta-card">
            <div class="meta-label">Participant</div>
            <div class="meta-value" id="self-name">$participant_name</div>
          </div>
          <div class="meta-card">
            <div class="meta-label">Role</div>
            <div class="meta-value" id="self-role">$participant_role</div>
          </div>
          <div class="meta-card">
            <div class="meta-label">Call State</div>
            <div class="meta-value" id="call-state">Idle</div>
          </div>
        </div>

        <div id="turn-warning" class="notice"$turn_warning_style>
          TURN is not configured for this deployment. Calls may fail on strict corporate, hospital, or carrier networks.
        </div>
      </section>

      <aside class="panel side-panel">
        <section class="participants">
          <h2>Participants</h2>
          <div id="participant-list" class="participant-list"></div>
        </section>

        <section class="chat">
          <h2>Room Chat</h2>
          <div id="chat-feed" class="chat-feed"></div>
          <div class="chat-form">
            <textarea id="chat-input" placeholder="Send a message to the consultation room"></textarea>
            <button id="send-chat" class="primary" type="button">Send</button>
          </div>
        </section>
      </aside>
    </div>
  </div>

  <script>
    const config = $config_json;
  </script>
  <script>
    (() => {
      const state = {
        ws: null,
        pc: null,
        localStream: null,
        remoteStream: new MediaStream(),
        participants: [],
        remoteParticipant: null,
        messageHistory: [],
        pendingCandidates: [],
        makingOffer: false,
        mediaStarted: false,
      };

      const elements = {
        startCall: document.getElementById("start-call"),
        toggleMic: document.getElementById("toggle-mic"),
        toggleCamera: document.getElementById("toggle-camera"),
        hangup: document.getElementById("hangup"),
        reconnect: document.getElementById("reconnect"),
        connectionStatus: document.getElementById("connection-status"),
        statusDot: document.getElementById("status-dot"),
        callState: document.getElementById("call-state"),
        participantList: document.getElementById("participant-list"),
        remoteVideo: document.getElementById("remote-video"),
        localVideo: document.getElementById("local-video"),
        remotePlaceholder: document.getElementById("remote-placeholder"),
        chatFeed: document.getElementById("chat-feed"),
        chatInput: document.getElementById("chat-input"),
        sendChat: document.getElementById("send-chat"),
        errorBanner: document.getElementById("error-banner"),
      };

      elements.remoteVideo.srcObject = state.remoteStream;

      function setError(message) {
        if (!message) {
          elements.errorBanner.classList.remove("visible");
          elements.errorBanner.textContent = "";
          return;
        }
        elements.errorBanner.textContent = message;
        elements.errorBanner.classList.add("visible");
      }

      function setConnectionStatus(message, isOnline) {
        elements.connectionStatus.textContent = message;
        elements.statusDot.classList.toggle("offline", !isOnline);
      }

      function setCallState(message) {
        elements.callState.textContent = message;
      }

      function wsUrl() {
        const scheme = window.location.protocol === "https:" ? "wss" : "ws";
        const params = new URLSearchParams({
          participant_id: config.participantId,
          role: config.role,
          display_name: config.displayName,
          token: config.token,
        });
        return `${scheme}://${window.location.host}/ws/consultations/${encodeURIComponent(config.roomId)}?${params.toString()}`;
      }

      function send(payload) {
        if (!state.ws || state.ws.readyState !== WebSocket.OPEN) {
          return;
        }
        state.ws.send(JSON.stringify(payload));
      }

      function participantLabel(role) {
        return role === "doctor" ? "Doctor" : "Patient";
      }

      function syncRemoteParticipant() {
        state.remoteParticipant = state.participants.find((item) => item.participant_id !== config.participantId) || null;
      }

      function renderParticipants() {
        elements.participantList.innerHTML = "";
        if (!state.participants.length) {
          const empty = document.createElement("div");
          empty.className = "participant-item";
          empty.textContent = "No one is connected yet.";
          elements.participantList.appendChild(empty);
          return;
        }

        state.participants.forEach((participant) => {
          const row = document.createElement("div");
          row.className = "participant-item";

          const copy = document.createElement("div");
          const name = document.createElement("div");
          name.className = "participant-name";
          name.textContent = participant.display_name;
          const role = document.createElement("div");
          role.className = "participant-role";
          role.textContent = participantLabel(participant.role) + (participant.participant_id === config.participantId ? " (You)" : "");
          copy.appendChild(name);
          copy.appendChild(role);

          const status = document.createElement("div");
          status.className = "participant-role";
          status.textContent = participant.media_ready ? "Media ready" : "Connected";

          row.appendChild(copy);
          row.appendChild(status);
          elements.participantList.appendChild(row);
        });
      }

      function renderMessages() {
        elements.chatFeed.innerHTML = "";
        if (!state.messageHistory.length) {
          const empty = document.createElement("div");
          empty.className = "chat-entry";
          empty.textContent = "No messages yet.";
          elements.chatFeed.appendChild(empty);
          return;
        }

        state.messageHistory.forEach((entry) => {
          const wrapper = document.createElement("div");
          wrapper.className = "chat-entry" + (entry.participant_id === config.participantId ? " me" : "");

          const meta = document.createElement("div");
          meta.className = "chat-meta";
          const author = document.createElement("span");
          author.className = "chat-author";
          author.textContent = entry.display_name;
          const timestamp = document.createElement("span");
          timestamp.textContent = entry.timestamp || "";
          meta.appendChild(author);
          meta.appendChild(timestamp);

          const text = document.createElement("div");
          text.className = "chat-text";
          text.textContent = entry.message;

          wrapper.appendChild(meta);
          wrapper.appendChild(text);
          elements.chatFeed.appendChild(wrapper);
        });

        elements.chatFeed.scrollTop = elements.chatFeed.scrollHeight;
      }

      function syncControls() {
        const hasMedia = !!state.localStream;
        const audioTrack = hasMedia ? state.localStream.getAudioTracks()[0] : null;
        const videoTrack = hasMedia ? state.localStream.getVideoTracks()[0] : null;

        elements.toggleMic.disabled = !audioTrack;
        elements.toggleCamera.disabled = !videoTrack;
        elements.hangup.disabled = !hasMedia;
        elements.toggleMic.textContent = audioTrack && audioTrack.enabled ? "Mute mic" : "Unmute mic";
        elements.toggleCamera.textContent = videoTrack && videoTrack.enabled ? "Turn off camera" : "Turn on camera";
        elements.startCall.textContent = hasMedia ? "Refresh media" : "Start camera and mic";
      }

      function updateRemotePlaceholder() {
        const hasRemoteTracks = state.remoteStream.getTracks().length > 0;
        const hasRemoteParticipant = !!state.remoteParticipant;
        elements.remotePlaceholder.style.display = hasRemoteTracks ? "none" : "flex";
        if (!hasRemoteTracks && hasRemoteParticipant) {
          elements.remotePlaceholder.querySelector(".placeholder-title").textContent = "Waiting for remote media";
        } else if (!hasRemoteTracks) {
          elements.remotePlaceholder.querySelector(".placeholder-title").textContent = "Waiting for the other participant";
        }
      }

      async function ensureLocalMedia() {
        setError("");
        if (state.localStream) {
          return state.localStream;
        }

        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
          throw new Error("This browser does not support camera and microphone access.");
        }

        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        state.localStream = stream;
        state.mediaStarted = true;
        elements.localVideo.srcObject = stream;
        syncControls();

        if (state.pc) {
          const senders = state.pc.getSenders();
          stream.getTracks().forEach((track) => {
            const exists = senders.some((sender) => sender.track && sender.track.kind === track.kind);
            if (!exists) {
              state.pc.addTrack(track, stream);
            }
          });
        }

        send({ type: "media_state", media_ready: true });
        return stream;
      }

      function resetRemoteStream() {
        state.remoteStream.getTracks().forEach((track) => track.stop());
        state.remoteStream = new MediaStream();
        elements.remoteVideo.srcObject = state.remoteStream;
        updateRemotePlaceholder();
      }

      function closePeerConnection() {
        if (state.pc) {
          state.pc.ontrack = null;
          state.pc.onicecandidate = null;
          state.pc.onconnectionstatechange = null;
          state.pc.close();
          state.pc = null;
        }
        state.pendingCandidates = [];
        resetRemoteStream();
        setCallState(state.localStream ? "Waiting for peer" : "Idle");
      }

      function stopLocalMedia() {
        if (!state.localStream) {
          return;
        }
        state.localStream.getTracks().forEach((track) => track.stop());
        state.localStream = null;
        elements.localVideo.srcObject = null;
        syncControls();
        send({ type: "media_state", media_ready: false });
      }

      async function ensurePeerConnection() {
        if (state.pc) {
          return state.pc;
        }

        const pc = new RTCPeerConnection({ iceServers: config.iceServers });
        state.pc = pc;

        if (state.localStream) {
          state.localStream.getTracks().forEach((track) => pc.addTrack(track, state.localStream));
        }

        pc.onicecandidate = (event) => {
          if (!event.candidate) {
            return;
          }
          send({
            type: "ice_candidate",
            candidate: event.candidate,
            target: state.remoteParticipant ? state.remoteParticipant.participant_id : null,
          });
        };

        pc.ontrack = (event) => {
          const knownTrackIds = new Set(state.remoteStream.getTracks().map((track) => track.id));
          event.streams[0].getTracks().forEach((track) => {
            if (!knownTrackIds.has(track.id)) {
              state.remoteStream.addTrack(track);
            }
          });
          elements.remoteVideo.srcObject = state.remoteStream;
          updateRemotePlaceholder();
        };

        pc.onconnectionstatechange = () => {
          const connectionState = pc.connectionState;
          if (connectionState === "connected") {
            setCallState("Connected");
          } else if (connectionState === "connecting") {
            setCallState("Connecting");
          } else if (connectionState === "failed") {
            setCallState("Connection failed");
          } else if (connectionState === "disconnected") {
            setCallState("Disconnected");
          } else if (connectionState === "closed") {
            setCallState("Closed");
          }
        };

        return pc;
      }

      async function flushPendingCandidates() {
        if (!state.pc || !state.pc.remoteDescription) {
          return;
        }
        while (state.pendingCandidates.length) {
          const candidate = state.pendingCandidates.shift();
          try {
            await state.pc.addIceCandidate(candidate);
          } catch (error) {
            console.error("Unable to add queued ICE candidate", error);
          }
        }
      }

      async function maybeCreateOffer() {
        if (config.role !== "doctor") {
          return;
        }
        if (!state.remoteParticipant || !state.localStream) {
          return;
        }
        if (!state.ws || state.ws.readyState !== WebSocket.OPEN) {
          return;
        }

        const pc = await ensurePeerConnection();
        if (state.makingOffer || pc.signalingState !== "stable") {
          return;
        }

        state.makingOffer = true;
        try {
          const offer = await pc.createOffer();
          await pc.setLocalDescription(offer);
          send({
            type: "offer",
            sdp: pc.localDescription,
            target: state.remoteParticipant.participant_id,
          });
          setCallState("Calling");
        } finally {
          state.makingOffer = false;
        }
      }

      async function handleRoomState(payload) {
        state.participants = payload.participants || [];
        state.messageHistory = payload.messages || [];
        syncRemoteParticipant();
        renderParticipants();
        renderMessages();
        updateRemotePlaceholder();
        if (state.remoteParticipant && state.localStream) {
          await maybeCreateOffer();
        }
      }

      async function handleOffer(payload) {
        if (payload.target && payload.target !== config.participantId) {
          return;
        }

        try {
          await ensureLocalMedia();
          const pc = await ensurePeerConnection();
          await pc.setRemoteDescription(new RTCSessionDescription(payload.sdp));
          await flushPendingCandidates();
          const answer = await pc.createAnswer();
          await pc.setLocalDescription(answer);
          send({ type: "answer", sdp: pc.localDescription, target: payload.from });
          setCallState("Answering");
        } catch (error) {
          console.error(error);
          setError(error.message || "Unable to answer the consultation call.");
        }
      }

      async function handleAnswer(payload) {
        if (!state.pc) {
          return;
        }
        if (payload.target && payload.target !== config.participantId) {
          return;
        }

        try {
          await state.pc.setRemoteDescription(new RTCSessionDescription(payload.sdp));
          await flushPendingCandidates();
          setCallState("Connected");
        } catch (error) {
          console.error(error);
          setError(error.message || "Unable to apply the remote answer.");
        }
      }

      async function handleIceCandidate(payload) {
        if (payload.target && payload.target !== config.participantId) {
          return;
        }

        const candidate = new RTCIceCandidate(payload.candidate);
        if (!state.pc || !state.pc.remoteDescription) {
          state.pendingCandidates.push(candidate);
          return;
        }

        try {
          await state.pc.addIceCandidate(candidate);
        } catch (error) {
          console.error(error);
        }
      }

      async function handleSignal(payload) {
        switch (payload.type) {
          case "room_state":
            await handleRoomState(payload);
            break;
          case "participant_joined":
          case "participant_left":
          case "media_state":
            state.participants = payload.participants || state.participants;
            syncRemoteParticipant();
            renderParticipants();
            updateRemotePlaceholder();
            if (payload.type === "participant_left" && !state.remoteParticipant) {
              closePeerConnection();
            }
            if (payload.type === "participant_joined") {
              await maybeCreateOffer();
            }
            break;
          case "offer":
            await handleOffer(payload);
            break;
          case "answer":
            await handleAnswer(payload);
            break;
          case "ice_candidate":
            await handleIceCandidate(payload);
            break;
          case "chat":
            state.messageHistory.push(payload.entry);
            renderMessages();
            break;
          case "hangup":
            closePeerConnection();
            break;
          case "error":
            setError(payload.message || "Consultation signaling error.");
            break;
          default:
            break;
        }
      }

      function connectSignaling() {
        setError("");
        setConnectionStatus("Connecting", false);

        if (state.ws) {
          state.ws.close();
        }

        const socket = new WebSocket(wsUrl());
        state.ws = socket;

        socket.addEventListener("open", () => {
          setConnectionStatus("Connected", true);
        });

        socket.addEventListener("message", async (event) => {
          try {
            const payload = JSON.parse(event.data);
            await handleSignal(payload);
          } catch (error) {
            console.error(error);
            setError("Received an invalid signaling message.");
          }
        });

        socket.addEventListener("close", () => {
          if (state.ws === socket) {
            setConnectionStatus("Disconnected", false);
          }
        });

        socket.addEventListener("error", () => {
          setConnectionStatus("Connection error", false);
        });
      }

      elements.startCall.addEventListener("click", async () => {
        try {
          await ensureLocalMedia();
          await maybeCreateOffer();
        } catch (error) {
          console.error(error);
          setError(error.message || "Unable to start camera and microphone.");
        }
      });

      elements.toggleMic.addEventListener("click", () => {
        if (!state.localStream) {
          return;
        }
        const track = state.localStream.getAudioTracks()[0];
        if (!track) {
          return;
        }
        track.enabled = !track.enabled;
        syncControls();
      });

      elements.toggleCamera.addEventListener("click", () => {
        if (!state.localStream) {
          return;
        }
        const track = state.localStream.getVideoTracks()[0];
        if (!track) {
          return;
        }
        track.enabled = !track.enabled;
        syncControls();
      });

      elements.hangup.addEventListener("click", () => {
        closePeerConnection();
        stopLocalMedia();
        send({ type: "hangup", target: state.remoteParticipant ? state.remoteParticipant.participant_id : null });
      });

      elements.reconnect.addEventListener("click", () => {
        connectSignaling();
      });

      function submitChat() {
        const message = elements.chatInput.value.trim();
        if (!message) {
          return;
        }
        send({ type: "chat", message });
        elements.chatInput.value = "";
      }

      elements.sendChat.addEventListener("click", submitChat);
      elements.chatInput.addEventListener("keydown", (event) => {
        if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
          submitChat();
        }
      });

      window.addEventListener("beforeunload", () => {
        if (state.ws) {
          state.ws.close();
        }
        closePeerConnection();
        stopLocalMedia();
      });

      syncControls();
      renderParticipants();
      renderMessages();
      updateRemotePlaceholder();
      connectSignaling();
    })();
  </script>
</body>
</html>
"""
)


def render_consultation_page(
    *,
    room_id: str,
    participant_name: str,
    participant_role: str,
    participant_id: str,
    token: str,
    ice_servers: list[dict[str, Any]],
    turn_configured: bool,
) -> str:
    title = f"BioSync Consultation - {room_id}"
    config = {
        "roomId": room_id,
        "displayName": participant_name,
        "participantId": participant_id,
        "role": participant_role.lower(),
        "token": token,
        "iceServers": ice_servers,
    }
    return PAGE_TEMPLATE.substitute(
        page_title=escape(title),
        room_heading=escape("Live Video Consultation"),
        room_subtitle=escape(
            "Secure room-based doctor-patient call with direct browser media, signaling, and room chat."
        ),
        room_id=escape(room_id),
        participant_name=escape(participant_name),
        participant_role=escape(participant_role.title()),
        turn_warning_style="" if not turn_configured else ' style="display:none;"',
        config_json=json.dumps(config),
    )
