export default {
  async fetch(request, env) {
    const url     = new URL(request.url);
    const token   = url.searchParams.get("token");
    const subject = url.searchParams.get("subject") || "SAMA Daily";
    const body    = url.searchParams.get("body");

    if (token !== env.RELAY_TOKEN) {
      return new Response("Unauthorized", { status: 401 });
    }

    if (!body) {
      return new Response("Missing body param", { status: 400 });
    }

    const res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "Authorization": "Bearer " + env.RESEND_API_KEY,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        from: "onboarding@resend.dev",
        to: ["tahirinavid@gmail.com"],
        subject: subject,
        html: body
      })
    });

    const data = await res.json();

    if (!res.ok) {
      return new Response("Resend error: " + JSON.stringify(data), { status: 502 });
    }

    return new Response("OK: " + data.id, { status: 200 });
  }
};
