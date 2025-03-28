const activeSessions: Record<string, string> = {}; // username -> sessionId

export const registerSession = (username: string, sessionId: string) => {
  activeSessions[username] = sessionId;
};

export const isSessionActive = (username: string, sessionId: string) => {
  return activeSessions[username] === sessionId;
};

export const terminateOtherSessions = (username: string, currentSessionId: string) => {
  if (activeSessions[username] && activeSessions[username] !== currentSessionId) {
    activeSessions[username] = currentSessionId;
  }
};
