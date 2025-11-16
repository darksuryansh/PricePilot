import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface PriceHistoryChartProps {
  data: Array<any>;
  view: 'daily' | 'monthly' | 'yearly';
}

export function PriceHistoryChart({ data, view }: PriceHistoryChartProps) {
  const xAxisKey = view === 'daily' ? 'date' : view === 'monthly' ? 'month' : 'year';

  console.log('🎨 Chart rendering with data:', data);
  console.log('🎨 Chart view:', view);

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis 
          dataKey={xAxisKey} 
          stroke="#6b7280"
          style={{ fontSize: '12px' }}
        />
        <YAxis 
          stroke="#6b7280"
          style={{ fontSize: '12px' }}
          tickFormatter={(value) => `₹${(value / 1000).toFixed(0)}k`}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: 'white',
            border: '2px solid #e5e7eb',
            borderRadius: '8px',
            fontSize: '12px'
          }}
          formatter={(value: any) => value ? [`₹${value.toLocaleString()}`, ''] : ['No data', '']}
          labelStyle={{ fontWeight: 600, marginBottom: '4px' }}
        />
        <Legend 
          wrapperStyle={{ fontSize: '12px' }}
          iconType="line"
        />
        <Line 
          type="monotone" 
          dataKey="amazon" 
          stroke="#FF9900" 
          strokeWidth={3}
          dot={{ fill: '#FF9900', r: 6, strokeWidth: 2, stroke: '#fff' }}
          activeDot={{ r: 8, strokeWidth: 2 }}
          name="Amazon"
          connectNulls={true}
        />
        <Line 
          type="monotone" 
          dataKey="flipkart" 
          stroke="#2874F0" 
          strokeWidth={3}
          dot={{ fill: '#2874F0', r: 6, strokeWidth: 2, stroke: '#fff' }}
          activeDot={{ r: 8, strokeWidth: 2 }}
          name="Flipkart"
          connectNulls={true}
        />
        <Line 
          type="monotone" 
          dataKey="myntra" 
          stroke="#FF3F6C" 
          strokeWidth={3}
          dot={{ fill: '#FF3F6C', r: 6, strokeWidth: 2, stroke: '#fff' }}
          activeDot={{ r: 8, strokeWidth: 2 }}
          name="Myntra"
          connectNulls={true}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
