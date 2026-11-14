---
name: zotero-fetch-pdfs
description: Find and attach missing PDFs for items in a Zotero collection, using Claude in Chrome and the user's library proxy. Use when the user asks to fetch, find, or download PDFs for Zotero items, or points at a "missing PDFs" collection.
---

# Fetch missing PDFs into Zotero

Tools: `mcp__zotero__*` for the library (the
[zotero-mcp](https://github.com/54yyyu/zotero-mcp) server, registered as `zotero`), `mcp__claude-in-chrome__*` for downloads
(the user's Chrome holds the library sign-in). Load the Chrome tools in one ToolSearch
call, including `browser_batch`, `javascript_tool`, `get_page_text` and `find`.

## Steps

1. `zotero_search_collections` → collection key; `zotero_get_collection_items`;
   `zotero_get_item_metadata` (include_abstract=false) for each item to get DOIs.
   Skip items that already have a PDF child.
2. Open every page through the user's library proxy, which also works off
   campus. Take its login prefix from the user's instructions, or ask once.
   For an EZproxy library it looks like
   `https://login.ezproxy.<library>/login?url=https://doi.org/<DOI>`, and the
   proxied host becomes e.g. `pubs-aip-org.ezproxy.<library>`.
   If the proxy asks for a login, stop and ask the user to sign in.
3. Get the PDF URL for the publisher (see table), navigate a tab to it, then save it
   from the page with:
   ```js
   const r = await fetch(location.href); const b = await r.blob();
   const a = document.createElement('a'); a.href = URL.createObjectURL(b);
   a.download = '<FirstAuthor>_<Year>_<JournalAbbrev>.pdf'; document.body.appendChild(a); a.click();
   [r.status, b.type, b.size]
   ```
   When fetching a URL other than the current page, check that the first 5 bytes are `%PDF-`
   before saving; publishers return HTML "Get Access" pages with status 200.
4. **Use a new tab for each download.** Chrome silently blocks a second automatic
   download from the same tab. Create all tabs up front with `tabs_create_mcp`
   (its tab IDs only come back when a batch ends).
5. Check each file in `~/Downloads`: `head -c5` is `%PDF-` and
   `pdftotext -l 1 <file> - | head` shows the right title.
6. `zotero_attach_file(item_key, file_path=<absolute path>)`, then confirm with
   `zotero_get_item_children` on all keys in one call.
7. Close the tabs you opened. If the user wants the downloads cleaned up, move them
   to `~/.Trash` rather than `rm`, after confirming the attachments exist.

## Publisher notes

| Publisher | Where the PDF is |
|---|---|
| AIP (JCP, 10.1063) | `meta[name=citation_pdf_url]` on the article page; redirects to a signed `watermark02.silverchair.com` URL. Has worked directly from doi.org, without the proxy. |
| Elsevier / ScienceDirect (10.1016) | Through the proxy, `/science/article/pii/<PII>/pdf` redirects to `pdf.sciencedirectassets.com`. A "Purchase PDF" link means the library has no access. Without the proxy, Cloudflare shows "Just a moment..." and blocks. |
| Wiley (10.1002) | Navigate to `/doi/pdfdirect/<DOI>?download=true` through the proxy; Chrome saves it as "<Journal> - <Year> - <Author> - <Title>.pdf", so rename it. The article page often renders blank and screenshots time out; ignore that. |
| Taylor & Francis (10.1080) | `/doi/pdf/<DOI>` through the proxy. A title ending in "Get Access" means the library has no access. |

## When there is no access

Search Google Scholar for the quoted title and look for a `[PDF]` link on the right
(`.gs_or_ggsm a`). If there is none, report the item as unavailable with the reason.
Do not buy articles, enter credentials, solve CAPTCHAs, or use shadow libraries.

## What not to do

- Don't stream PDF bytes to a local HTTP server from the page; the auto-mode
  classifier blocks it as exposing a local service.
- Don't click the Chrome PDF viewer's download button; it saves nothing that can be found.
