//! 记忆检索模块 / Memory Search Module
//!
//! 提供基于 FAISS 的向量相似度搜索功能。
//! Provides FAISS-based vector similarity search functionality.
//!
//! # Reference / 参考
//!
//! - PRD §0.4: 混合存储系统
//! - MOD-RustCore.md §4.1: MemorySearcher
//!
//! # Usage / 使用示例
//!
//! ```python
//! from rainze_core.memory import VectorIndex
//!
//! # 创建索引 / Create index
//! index = VectorIndex.new(dimension=768)
//!
//! # 添加向量 / Add vectors
//! vectors = [[0.1, 0.2, ...], [0.3, 0.4, ...]]
//! ids = index.add_vectors(vectors)
//!
//! # 搜索 / Search
//! query = [0.15, 0.25, ...]
//! results = index.search(query, k=5)
//!
//! # 保存/加载 / Save/Load
//! index.save("./data/faiss_index.bin")
//! index = VectorIndex.load("./data/faiss_index.bin")
//! ```

use faiss::{index_factory, Index, MetricType};
use pyo3::prelude::*;
use std::sync::{Arc, Mutex};

/// FAISS 向量索引封装 / FAISS Vector Index Wrapper
///
/// 使用 IndexFlatIP (内积相似度) 实现语义检索。
/// Uses IndexFlatIP (inner product similarity) for semantic search.
///
/// # Thread Safety / 线程安全
///
/// 使用 Arc<Mutex<>> 包装以支持多线程访问。
/// Wrapped with Arc<Mutex<>> for multi-threaded access.
#[pyclass]
pub struct VectorIndex {
    index: Arc<Mutex<faiss::index::IndexImpl>>,
    dimension: u32,
}

#[pymethods]
impl VectorIndex {
    /// 创建新的向量索引 / Create new vector index
    ///
    /// # Arguments / 参数
    ///
    /// - `dimension`: 向量维度 / Vector dimension (e.g., 768)
    ///
    /// # Returns / 返回
    ///
    /// 新的 VectorIndex 实例 / New VectorIndex instance
    #[staticmethod]
    fn new(dimension: u32) -> PyResult<Self> {
        // 使用 Flat 索引和内积相似度 / Use Flat index with inner product
        let index = index_factory(dimension, "Flat", MetricType::InnerProduct)
            .map_err(|e| {
                pyo3::exceptions::PyRuntimeError::new_err(format!(
                    "Failed to create FAISS index: {}",
                    e
                ))
            })?;

        Ok(VectorIndex {
            index: Arc::new(Mutex::new(index)),
            dimension,
        })
    }

    /// 添加向量到索引 / Add vectors to index
    ///
    /// # Arguments / 参数
    ///
    /// - `vectors`: 向量列表 / List of vectors
    ///
    /// # Returns / 返回
    ///
    /// 添加的向量 ID 列表 / List of added vector IDs
    fn add_vectors(&self, vectors: Vec<Vec<f32>>) -> PyResult<Vec<i64>> {
        // 验证向量维度 / Validate vector dimensions
        for (i, vec) in vectors.iter().enumerate() {
            if vec.len() != self.dimension as usize {
                return Err(pyo3::exceptions::PyValueError::new_err(format!(
                    "Vector {} has dimension {}, expected {}",
                    i,
                    vec.len(),
                    self.dimension
                )));
            }
        }

        // 展平向量 / Flatten vectors
        let flat_vectors: Vec<f32> =
            vectors.iter().flat_map(|v| v.iter().copied()).collect();

        // 获取锁并添加 / Lock and add
        let mut index = self.index.lock().map_err(|e| {
            pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e))
        })?;

        let start_id = index.ntotal() as i64;

        index.add(&flat_vectors).map_err(|e| {
            pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to add vectors: {}", e))
        })?;

        let end_id = index.ntotal() as i64;

        // 返回 ID 列表 / Return ID list
        Ok((start_id..end_id).collect())
    }

    /// 搜索最相似的向量 / Search for most similar vectors
    ///
    /// # Arguments / 参数
    ///
    /// - `query`: 查询向量 / Query vector
    /// - `k`: 返回的结果数量 / Number of results
    ///
    /// # Returns / 返回
    ///
    /// 元组列表 (ID, 相似度分数) / List of tuples (ID, score)
    fn search(&self, query: Vec<f32>, k: usize) -> PyResult<Vec<(faiss::Idx, f32)>> {
        // 验证查询向量维度 / Validate query dimension
        if query.len() != self.dimension as usize {
            return Err(pyo3::exceptions::PyValueError::new_err(format!(
                "Query has dimension {}, expected {}",
                query.len(),
                self.dimension
            )));
        }

        // 获取锁并搜索 / Lock and search
        let index = self.index.lock().map_err(|e| {
            pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e))
        })?;

        let result = index.search(&query, k).map_err(|e| {
            pyo3::exceptions::PyRuntimeError::new_err(format!("Search failed: {}", e))
        })?;

        // 组装结果 / Assemble results
        let results: Vec<(faiss::Idx, f32)> = result
            .labels
            .iter()
            .zip(result.distances.iter())
            .map(|(&id, &score)| (id, score))
            .collect();

        Ok(results)
    }

    /// 保存索引到文件 / Save index to file
    fn save(&self, path: &str) -> PyResult<()> {
        let index = self.index.lock().map_err(|e| {
            pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e))
        })?;

        faiss::write_index(&*index, path).map_err(|e| {
            pyo3::exceptions::PyIOError::new_err(format!("Failed to save index: {}", e))
        })?;

        Ok(())
    }

    /// 从文件加载索引 / Load index from file
    #[staticmethod]
    fn load(path: &str) -> PyResult<Self> {
        let index = faiss::read_index(path).map_err(|e| {
            pyo3::exceptions::PyIOError::new_err(format!("Failed to load index: {}", e))
        })?;

        let dimension = index.d();

        Ok(VectorIndex {
            index: Arc::new(Mutex::new(index)),
            dimension,
        })
    }

    /// 获取索引中的向量数量 / Get number of vectors
    fn ntotal(&self) -> PyResult<i64> {
        let index = self.index.lock().map_err(|e| {
            pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e))
        })?;

        // FAISS 的 ntotal() 返回 usize，需要转换为 i64
        let ntotal = index.ntotal() as i64;
        Ok(ntotal)
    }

    /// 获取向量维度 / Get vector dimension
    fn dimension(&self) -> u32 {
        self.dimension
    }

    /// 重置索引（清空所有向量）/ Reset index
    fn reset(&self) -> PyResult<()> {
        let mut index = self.index.lock().map_err(|e| {
            pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e))
        })?;

        index.reset().map_err(|e| {
            pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to reset index: {}", e))
        })?;

        Ok(())
    }
}

/// Python 模块注册 / Python module registration
pub fn register_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    let memory_module = PyModule::new(m.py(), "memory")?;
    memory_module.add_class::<VectorIndex>()?;
    m.add_submodule(&memory_module)?;
    Ok(())
}
