import { ReactFlow, Background, Controls } from '@xyflow/react';
import {type Node, type Edge} from '@xyflow/react';
import { Component, ReactNode } from 'react';

export class GraphEditor extends Component {
    render(): ReactNode {
        const initialNodes: Node[] = [
            { id: '1', data: { label: 'Node 1' }, position: { x: 5, y: 5 } },
            { id: '2', data: { label: 'Node 2' }, position: { x: 5, y: 100 } },
          ];
           
        const initialEdges: Edge[] = [{ id: 'e1-2', source: '1', target: '2' }];

        return (
            <ReactFlow nodes={initialNodes} edges={initialEdges}>
                <Background />
                <Controls />
            </ReactFlow>
        )

    }
}
// export const Graph = (nodes: Node[], edges: Edge[]) => {
//     return 
// }