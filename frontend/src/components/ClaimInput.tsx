'use client';

import { useState } from 'react';
import { Claim, ProcedureCode } from '@/lib/types';

interface ClaimInputProps {
  onSubmit: (claim: Claim) => void;
  isLoading: boolean;
}

export default function ClaimInput({ onSubmit, isLoading }: ClaimInputProps) {
  const [formData, setFormData] = useState({
    claim_id: '',
    patient_name: '',
    patient_dob: '',
    patient_gender: 'M' as 'M' | 'F',
    insurance_id: '',
    provider_name: '',
    provider_npi: '',
    provider_specialty: '',
    service_date: '',
    diagnosis_codes: '',
  });

  const [procedures, setProcedures] = useState<Array<{
    cpt: string;
    modifiers: string;
    units: string;
    charge: string;
  }>>([{ cpt: '', modifiers: '', units: '1', charge: '' }]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const procedureCodes: ProcedureCode[] = procedures.map(p => ({
      cpt: p.cpt,
      modifiers: p.modifiers ? p.modifiers.split(',').map(m => m.trim()) : [],
      units: parseInt(p.units) || 1,
      charge: parseFloat(p.charge) || 0,
    }));

    const totalCharge = procedureCodes.reduce((sum, p) => sum + p.charge * p.units, 0);

    const claim: Claim = {
      claim_id: formData.claim_id,
      patient: {
        name: formData.patient_name,
        dob: formData.patient_dob,
        gender: formData.patient_gender,
        insurance_id: formData.insurance_id,
      },
      provider: {
        name: formData.provider_name,
        npi: formData.provider_npi,
        specialty: formData.provider_specialty,
      },
      service_date: formData.service_date,
      diagnosis_codes: formData.diagnosis_codes.split(',').map(c => c.trim()).filter(c => c),
      procedure_codes: procedureCodes,
      total_charge: totalCharge,
    };

    onSubmit(claim);
  };

  const loadSampleClaim = () => {
    setFormData({
      claim_id: 'CLM001',
      patient_name: 'John Doe',
      patient_dob: '1985-05-15',
      patient_gender: 'M',
      insurance_id: 'XYZ123456789',
      provider_name: 'Dr. Jane Smith',
      provider_npi: '1234567890',
      provider_specialty: 'Family Medicine',
      service_date: '2025-01-15',
      diagnosis_codes: 'E11.9',
    });
    setProcedures([{ cpt: '99213', modifiers: '', units: '1', charge: '135' }]);
  };

  const loadInvalidClaim = () => {
    setFormData({
      claim_id: 'CLM002',
      patient_name: 'Jane Test',
      patient_dob: '2020-01-01',
      patient_gender: 'F',
      insurance_id: 'TEST123456789',
      provider_name: 'Dr. Test',
      provider_npi: '9999999999',
      provider_specialty: 'Testing',
      service_date: '2025-01-15',
      diagnosis_codes: 'Z00.00',
    });
    setProcedures([
      { cpt: '99205', modifiers: '', units: '1', charge: '500' },
      { cpt: '99213', modifiers: '', units: '1', charge: '135' },
    ]);
  };

  const addProcedure = () => {
    setProcedures([...procedures, { cpt: '', modifiers: '', units: '1', charge: '' }]);
  };

  const removeProcedure = (index: number) => {
    setProcedures(procedures.filter((_, i) => i !== index));
  };

  const updateProcedure = (index: number, field: string, value: string) => {
    const updated = [...procedures];
    updated[index] = { ...updated[index], [field]: value };
    setProcedures(updated);
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Enter Claim Data</h2>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={loadSampleClaim}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            Load Valid Sample
          </button>
          <button
            type="button"
            onClick={loadInvalidClaim}
            className="text-sm text-red-600 hover:text-red-800"
          >
            Load Invalid Sample
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Claim ID */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Claim ID</label>
          <input
            type="text"
            value={formData.claim_id}
            onChange={(e) => setFormData({ ...formData, claim_id: e.target.value })}
            className="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        {/* Patient Information */}
        <div className="border-t pt-4">
          <h3 className="text-lg font-medium mb-3">Patient Information</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
              <input
                type="text"
                value={formData.patient_name}
                onChange={(e) => setFormData({ ...formData, patient_name: e.target.value })}
                className="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Date of Birth</label>
              <input
                type="date"
                value={formData.patient_dob}
                onChange={(e) => setFormData({ ...formData, patient_dob: e.target.value })}
                className="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Gender</label>
              <select
                value={formData.patient_gender}
                onChange={(e) => setFormData({ ...formData, patient_gender: e.target.value as 'M' | 'F' })}
                className="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="M">Male</option>
                <option value="F">Female</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Insurance ID</label>
              <input
                type="text"
                value={formData.insurance_id}
                onChange={(e) => setFormData({ ...formData, insurance_id: e.target.value })}
                className="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
          </div>
        </div>

        {/* Provider Information */}
        <div className="border-t pt-4">
          <h3 className="text-lg font-medium mb-3">Provider Information</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Provider Name</label>
              <input
                type="text"
                value={formData.provider_name}
                onChange={(e) => setFormData({ ...formData, provider_name: e.target.value })}
                className="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">NPI (10 digits)</label>
              <input
                type="text"
                value={formData.provider_npi}
                onChange={(e) => setFormData({ ...formData, provider_npi: e.target.value })}
                className="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                pattern="[0-9]{10}"
                required
              />
            </div>
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Specialty</label>
              <input
                type="text"
                value={formData.provider_specialty}
                onChange={(e) => setFormData({ ...formData, provider_specialty: e.target.value })}
                className="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
          </div>
        </div>

        {/* Service Details */}
        <div className="border-t pt-4">
          <h3 className="text-lg font-medium mb-3">Service Details</h3>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">Service Date</label>
            <input
              type="date"
              value={formData.service_date}
              onChange={(e) => setFormData({ ...formData, service_date: e.target.value })}
              className="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Diagnosis Codes (comma-separated)
            </label>
            <input
              type="text"
              value={formData.diagnosis_codes}
              onChange={(e) => setFormData({ ...formData, diagnosis_codes: e.target.value })}
              placeholder="E11.9, I10"
              className="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
        </div>

        {/* Procedure Codes */}
        <div className="border-t pt-4">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-lg font-medium">Procedure Codes</h3>
            <button
              type="button"
              onClick={addProcedure}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              + Add Procedure
            </button>
          </div>
          {procedures.map((proc, index) => (
            <div key={index} className="mb-4 p-4 bg-gray-50 rounded-md">
              <div className="flex gap-3 items-end">
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">CPT Code</label>
                  <input
                    type="text"
                    value={proc.cpt}
                    onChange={(e) => updateProcedure(index, 'cpt', e.target.value)}
                    className="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Modifiers</label>
                  <input
                    type="text"
                    value={proc.modifiers}
                    onChange={(e) => updateProcedure(index, 'modifiers', e.target.value)}
                    placeholder="25,59"
                    className="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="w-20">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Units</label>
                  <input
                    type="number"
                    value={proc.units}
                    onChange={(e) => updateProcedure(index, 'units', e.target.value)}
                    min="1"
                    className="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div className="w-32">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Charge ($)</label>
                  <input
                    type="number"
                    value={proc.charge}
                    onChange={(e) => updateProcedure(index, 'charge', e.target.value)}
                    step="0.01"
                    min="0"
                    className="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                {procedures.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeProcedure(index)}
                    className="px-3 py-2 text-red-600 hover:text-red-800 text-2xl leading-none"
                    title="Remove procedure"
                  >
                    ×
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 font-medium"
        >
          {isLoading ? 'Validating...' : 'Validate Claim'}
        </button>
      </form>
    </div>
  );
}
