routerAdd("GET", "/static/*", $apis.staticDirectoryHandler("./pb_public/static", false))

routerAdd("GET", "/", (c) => {
    try {
    const define = require(`${__hooks}/define.js`)
    
    const html = $template.loadFiles(
        `${__hooks}/views/index.html`,
    ).render({
    })

    return c.html(200, html)}
    catch (e) { console.log(e); return c.string(500, `${e.stack}`) }
})
routerAdd("GET", "/premiya/", (c) => {
    try {
    const define = require(`${__hooks}/define.js`)
    
    const html = $template.loadFiles(
        `${__hooks}/views/premiya.html`,
    ).render({
    })

    return c.html(200, html)}
    catch (e) { console.log(e); return c.string(500, `${e.stack}`) }
})
routerAdd("GET", "/magazine/", (c) => {
    try {
    const define = require(`${__hooks}/define.js`)
    
    const html = $template.loadFiles(
        `${__hooks}/views/magazine.html`,
    ).render({
    })

    return c.html(200, html)}
    catch (e) { console.log(e); return c.string(500, `${e.stack}`) }
})
routerAdd("GET", "/sponsorstvo/", (c) => {
    try {
    const define = require(`${__hooks}/define.js`)
    
    const html = $template.loadFiles(
        `${__hooks}/views/sponsorstvo.html`,
    ).render({
    })

    return c.html(200, html)}
    catch (e) { console.log(e); return c.string(500, `${e.stack}`) }
})
routerAdd("GET", "/sudeystvo/", (c) => {
    try {
    const define = require(`${__hooks}/define.js`)
    
    const html = $template.loadFiles(
        `${__hooks}/views/sudeystvo.html`,
    ).render({
    })

    return c.html(200, html)}
    catch (e) { console.log(e); return c.string(500, `${e.stack}`) }
})
routerAdd("GET", "/participants/", (c) => {
    try {
    const define = require(`${__hooks}/define.js`)
    
    const html = $template.loadFiles(
        `${__hooks}/views/participants.html`,
    ).render({
    })

    return c.html(200, html)}
    catch (e) { console.log(e); return c.string(500, `${e.stack}`) }
})
routerAdd("GET", "/uchastie/", (c) => {
    try {
    const define = require(`${__hooks}/define.js`)
    
    const html = $template.loadFiles(
        `${__hooks}/views/uchastie.html`,
    ).render({
    })

    return c.html(200, html)}
    catch (e) { console.log(e); return c.string(500, `${e.stack}`) }
})
routerAdd("POST", "/unload", (c) =>{
    try{
        const define = require(`${__hooks}/define.js`)
        const data = $apis.requestInfo(c).data
        define.updateOrCreateOfKey("userstate", "user_id", data.user_id, {
            "user_id": data.user_id,
            "boostpropstapcounter": data.user_count_now,
            "tickets": data.tickets
        })
        define.updateOrCreateOfKey("farmtracking", "user_id", data.user_id, {
            "user_id": data.user_id,
            "click": data.click,
            "start_farm": data.start_farm,
            "end_farm": data.end_farm,
            "click_before5min": data.click_before5min,
            "ads_reduce60": data.ads_reduce60,
            "ads_reduce30": data.ads_reduce30,
            "reward_ticket": data.reward_ticket,
            "reward_ads_ticket": data.reward_ads_ticket
        })
        return c.redirect(302, "/")
    }
    catch (e) { console.log(e); return c.string(500, `${e.stack}`) }
})
