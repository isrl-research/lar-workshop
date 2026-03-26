local function make_contributor_blocks(meta)
  if not meta.contributors then return nil end

  local items = pandoc.List()
  for _, cont in ipairs(meta.contributors) do
    local name = pandoc.utils.stringify(cont.name)
    local role = pandoc.utils.stringify(cont.role)
    items:insert({
      pandoc.Plain({
        pandoc.Str(name),
        pandoc.Space(),
        pandoc.Str("·"),
        pandoc.Space(),
        pandoc.Emph({pandoc.Str(role)})
      })
    })
  end

  return pandoc.List({
    pandoc.Para({pandoc.SmallCaps({pandoc.Str("Contributors")})}),
    pandoc.BulletList(items)
  })
end

function Pandoc(doc)
  local blocks = make_contributor_blocks(doc.meta)
  if not blocks then return doc end

  -- insert at position 1 so it appears just below the title block
  for i = #blocks, 1, -1 do
    doc.blocks:insert(1, blocks[i])
  end
  return doc
end