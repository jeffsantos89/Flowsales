import { useEffect, useState, useMemo, useCallback } from 'react';
import { toast } from 'react-toastify'; // Adicione react-toastify para notificações
import { useQuery, useQueryClient } from 'react-query'; // Adicione react-query para gerenciamento de estado
import api from '../services/api';
import { Spinner } from '../components/Spinner'; // Crie um componente de loading
import { ErrorBoundary } from '../components/ErrorBoundary'; // Crie um componente para tratamento de erros

// Tipos
export interface Lead {
    id: string;
    name: string;
    email: string;
    stage: LeadStage;
    score: number;
    phone?: string;
    createdAt: string;
}

export enum LeadStage {
    NEW = 'novo',
    QUALIFIED = 'qualificado',
    PROPOSAL = 'proposta',
    CLOSED = 'fechado',
}

// Componentes isolados
const LeadFilters = ({ 
    filter, 
    setFilter, 
    stageFilter, 
    setStageFilter 
}: {
    filter: string;
    setFilter: (value: string) => void;
    stageFilter: string;
    setStageFilter: (value: string) => void;
}) => (
    <div className="flex gap-4">
        <input
            type="text"
            placeholder="Filtrar por nome ou e-mail"
            className="border p-2 rounded w-1/2 focus:ring-2 focus:ring-blue-500"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
        />
        <select
            className="border p-2 rounded focus:ring-2 focus:ring-blue-500"
            value={stageFilter}
            onChange={(e) => setStageFilter(e.target.value)}
        >
            <option value="">Todos os estágios</option>
            {Object.values(LeadStage).map((stage) => (
                <option key={stage} value={stage}>{stage}</option>
          <option value="novo">Novo</option>
          <option value="qualificado">Qualificado</option>
          <option value="proposta">Proposta</option>
          <option value="fechado">Fechado</option>
        </select>
      </div>

      <table className="w-full table-auto text-sm border rounded overflow-hidden">
        <thead className="bg-gray-200">
          <tr>
            <th className="p-2">Nome</th>
            <th>Email</th>
            <th>Telefone</th>
            <th>Estágio</th>
            <th>Score</th>
            <th>Data</th>
          </tr>
        </thead>
        <tbody>
          {filteredLeads.map((lead) => (
            <tr key={lead.id} className="border-t">
              <td className="p-2">{lead.name}</td>
              <td>{lead.email}</td>
              <td>{lead.phone || '-'}</td>
              <td>{lead.stage}</td>
              <td>{lead.score}</td>
              <td>{new Date(lead.createdAt).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
