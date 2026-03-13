// src/api/findReplace.js
import axiosInstance from './axiosInstance'

export async function findReplaceSearch(pattern, replacement, flags, scope) {
  const res = await axiosInstance.post('/api/admin/find-replace/search', {
    pattern,
    replacement,
    flags,
    scope,
  })
  return res.data
}

export async function findReplaceExecute(pattern, replacement, flags, hits) {
  const res = await axiosInstance.post('/api/admin/find-replace/replace', {
    pattern,
    replacement,
    flags,
    hits,
  })
  return res.data
}
